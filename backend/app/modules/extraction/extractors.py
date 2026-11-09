from __future__ import annotations

import csv
import io
import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.core.config import Settings, get_settings


logger = logging.getLogger(__name__)


class ExtractionError(RuntimeError):
	pass


class CapabilityUnavailable(ExtractionError):
	pass


@dataclass(frozen=True)
class ExtractedPage:
	page_number: int
	text: str
	method: str
	confidence: float | None = None
	status: str = "completed"
	ocr_used: bool = False
	error_summary: str | None = None


class DocumentExtractor(Protocol):
	extractor_type: str
	extractor_version: str

	def extract(self, content: bytes) -> list[ExtractedPage]: ...


class TextExtractor:
	extractor_type = "text"
	extractor_version = "stdlib-1"

	def extract(self, content: bytes) -> list[ExtractedPage]:
		for encoding in ("utf-8-sig", "utf-16", "cp1252"):
			try:
				return [ExtractedPage(1, content.decode(encoding), self.extractor_type)]
			except UnicodeDecodeError:
				continue
		raise ExtractionError("Text encoding is not supported")


class CsvExtractor:
	extractor_type = "csv"
	extractor_version = "stdlib-1"

	def extract(self, content: bytes) -> list[ExtractedPage]:
		text = TextExtractor().extract(content)[0].text
		try:
			rows = csv.reader(io.StringIO(text))
			formatted = ["\t".join(row) for row in rows]
		except csv.Error as exc:
			raise ExtractionError("CSV content could not be decoded") from exc
		return [ExtractedPage(1, "\n".join(formatted), self.extractor_type)]


def _usable_text(text: str, minimum_characters: int = 3) -> bool:
	return len(" ".join(text.split())) >= minimum_characters


def _tesseract_executable(settings: Settings) -> str | None:
	return settings.tesseract_cmd or shutil.which("tesseract")


def available_ocr_languages(settings: Settings | None = None) -> dict[str, object]:
	settings = settings or get_settings()
	executable = _tesseract_executable(settings)
	if executable is None:
		return {"available": False, "executable": None, "languages": [], "configured": settings.configured_ocr_languages}
	try:
		result = subprocess.run(
			[executable, "--list-langs"], capture_output=True, text=True, check=True,
			timeout=settings.ocr_timeout_seconds,
		)
	except (OSError, subprocess.SubprocessError):
		return {"available": False, "executable": executable, "languages": [], "configured": settings.configured_ocr_languages}
	languages = [line.strip() for line in result.stdout.splitlines() if line.strip() and not line.startswith("List of")]
	return {
		"available": True,
		"executable": executable,
		"languages": languages,
		"configured": settings.configured_ocr_languages,
	}


class ImageOcrExtractor:
	extractor_type = "tesseract"
	extractor_version = "cli-2"

	def __init__(self, language: str | None = None, settings: Settings | None = None) -> None:
		self.settings = settings or get_settings()
		self.language = language or self.settings.ocr_default_lang

	def extract(self, content: bytes) -> list[ExtractedPage]:
		return [self._run(content, 1)]

	def _run(self, content: bytes, page_number: int) -> ExtractedPage:
		executable = _tesseract_executable(self.settings)
		if executable is None:
			raise CapabilityUnavailable("Tesseract is not installed or configured")
		with tempfile.TemporaryDirectory(prefix="orvexa-ocr-") as directory:
			input_path = Path(directory) / "input.png"
			input_path.write_bytes(content)
			command = [executable, str(input_path), "stdout", "-l", self.language]
			if self.settings.tessdata_prefix:
				command.extend(["--tessdata-dir", self.settings.tessdata_prefix])
			try:
				result = subprocess.run(
					command, capture_output=True, check=True,
					timeout=self.settings.ocr_timeout_seconds,
				)
			except subprocess.TimeoutExpired as exc:
				raise ExtractionError("OCR timed out") from exc
			except FileNotFoundError as exc:
				raise CapabilityUnavailable("Tesseract is not installed or configured") from exc
			except subprocess.CalledProcessError as exc:
				message = exc.stderr.decode("utf-8", errors="replace")[:200]
				if "Failed loading language" in message or "Error opening data file" in message:
					raise CapabilityUnavailable("Configured OCR language data is unavailable") from exc
				raise ExtractionError("OCR failed") from exc
		return ExtractedPage(page_number, result.stdout.decode("utf-8", errors="replace"), self.extractor_type, ocr_used=True)


class PdfExtractor:
	extractor_type = "pdf"
	extractor_version = "pypdfium2-2"

	def __init__(self, settings: Settings | None = None) -> None:
		self.settings = settings or get_settings()

	def extract(self, content: bytes) -> list[ExtractedPage]:
		try:
			from pypdf import PdfReader
		except ImportError as exc:
			raise CapabilityUnavailable("PDF extraction requires the pypdf dependency") from exc
		try:
			reader = PdfReader(io.BytesIO(content))
			if reader.is_encrypted:
				raise ExtractionError("Encrypted PDFs are not supported")
			pages: list[ExtractedPage] = []
			for page_number, page in enumerate(reader.pages, 1):
				text = page.extract_text() or ""
				if _usable_text(text):
					pages.append(ExtractedPage(page_number, text, "native"))
					continue
				try:
					image = render_pdf_page(content, page_number, self.settings)
					pages.append(ImageOcrExtractor(settings=self.settings)._run(image, page_number))
				except CapabilityUnavailable as exc:
					pages.append(ExtractedPage(page_number, text, "native", status="failed", error_summary=str(exc)))
				except ExtractionError as exc:
					pages.append(ExtractedPage(page_number, text, "ocr", status="failed", error_summary=str(exc)))
			return pages
		except ExtractionError:
			raise
		except Exception as exc:
			raise ExtractionError("PDF extraction failed") from exc


class DocxExtractor:
	extractor_type = "docx"
	extractor_version = "python-docx-1"

	def extract(self, content: bytes) -> list[ExtractedPage]:
		try:
			from docx import Document as WordDocument
		except ImportError as exc:
			raise CapabilityUnavailable("DOCX extraction requires the python-docx dependency") from exc
		try:
			document = WordDocument(io.BytesIO(content))
			paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
			for table in document.tables:
				paragraphs.extend("\t".join(cell.text for cell in row.cells) for row in table.rows)
			return [ExtractedPage(1, "\n".join(paragraphs), self.extractor_type)]
		except Exception as exc:
			raise ExtractionError("DOCX extraction failed") from exc


def render_pdf_page(content: bytes, page_number: int, settings: Settings | None = None) -> bytes:
	try:
		import pypdfium2 as pdfium
		from PIL import Image  # noqa: F401
	except ImportError as exc:
		raise CapabilityUnavailable("PDF OCR rendering requires pypdfium2 and Pillow") from exc
	pdf = None
	page = None
	try:
		pdf = pdfium.PdfDocument(content)
		page = pdf.get_page(page_number - 1)
		image = page.render(scale=2.0).to_pil()
		max_pixels = (settings or get_settings()).ocr_max_image_pixels
		if image.width * image.height > max_pixels:
			ratio = (max_pixels / (image.width * image.height)) ** 0.5
			image = image.resize((max(1, int(image.width * ratio)), max(1, int(image.height * ratio))))
		output = io.BytesIO()
		image.save(output, format="PNG")
		return output.getvalue()
	finally:
		if page is not None:
			page.close()
		if pdf is not None:
			pdf.close()


class TesseractOcrExtractor:
	extractor_type = "tesseract"
	extractor_version = "cli-1"

	def __init__(self, language: str = "eng") -> None:
		self.language = language

	def extract(self, content: bytes) -> list[ExtractedPage]:
		executable = shutil.which("tesseract")
		if executable is None:
			raise CapabilityUnavailable("Tesseract is not installed")
		with tempfile.TemporaryDirectory() as directory:
			input_path = Path(directory) / "input.bin"
			input_path.write_bytes(content)
			try:
				result = subprocess.run(
					[executable, str(input_path), "stdout", "-l", self.language],
					capture_output=True,
					check=True,
					timeout=60,
				)
			except subprocess.TimeoutExpired as exc:
				raise ExtractionError("OCR timed out") from exc
			except subprocess.CalledProcessError as exc:
				message = exc.stderr.decode("utf-8", errors="replace")[:200]
				raise ExtractionError(f"OCR failed: {message}") from exc
		return [ExtractedPage(1, result.stdout.decode("utf-8", errors="replace"), self.extractor_type)]


def extractor_for(extension: str) -> DocumentExtractor:
	if extension == ".txt":
		return TextExtractor()
	if extension == ".csv":
		return CsvExtractor()
	if extension == ".pdf":
		return PdfExtractor()
	if extension == ".docx":
		return DocxExtractor()
	return ImageOcrExtractor()
