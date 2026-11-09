from io import BytesIO
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from docx import Document as WordDocument
import pytest
import pytest_asyncio
from pypdf import PdfWriter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.models import Role, User
from app.modules.documents.analysis_models import Analysis, DocumentProcessingJob
from app.modules.documents.document_models import Document, DocumentPage
from app.modules.extraction.models import DocumentExtraction
from app.modules.extraction.extractors import (
	CapabilityUnavailable,
	CsvExtractor,
	DocxExtractor,
	ExtractedPage,
	PdfExtractor,
	TextExtractor,
)
from app.modules.extraction.service import ExtractionService
from app.modules.documents.storage import LocalStorageProvider


@dataclass
class ControlledExtractor:
	pages: list
	extractor_type: str = "controlled"
	extractor_version: str = "test"

	def extract(self, content: bytes) -> list:
		return self.pages


@pytest_asyncio.fixture
async def extraction_context(tmp_path: Path):
	engine = create_async_engine(
		"sqlite+aiosqlite://",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
	)
	session_factory = async_sessionmaker(engine, expire_on_commit=False)
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)

	now = datetime.now(timezone.utc)
	document = Document(
		id=uuid4(),
		user_id=uuid4(),
		original_filename="report.txt",
		storage_key="report.txt",
		mime_type="text/plain",
		file_size=7,
		sha256_hash="a" * 64,
		document_type="txt",
		processing_status="queued",
		extraction_status="pending",
		created_at=now,
		updated_at=now,
	)

	async with session_factory() as session:
		session.add(document)
		await session.commit()
		yield session, document, tmp_path

	await engine.dispose()


async def run_controlled_extraction(
	extraction_context: tuple[AsyncSession, Document, Path],
	monkeypatch: pytest.MonkeyPatch,
	pages: list,
):
	session, document, storage_root = extraction_context
	extractor = ControlledExtractor(pages)
	monkeypatch.setattr("app.modules.extraction.service.extractor_for", lambda _: extractor)
	storage = LocalStorageProvider(storage_root)
	await storage.save(document.storage_key, b"content")
	extraction = await ExtractionService(session, storage).extract(document)
	persisted_pages = list(
		await session.scalars(
			select(DocumentPage)
			.where(DocumentPage.document_id == document.id)
			.order_by(DocumentPage.page_number)
		)
	)
	return extraction, persisted_pages


@pytest.mark.asyncio
async def test_extraction_persists_page_text_and_existing_metadata(extraction_context, monkeypatch) -> None:
	from app.modules.extraction.extractors import ExtractedPage

	extraction, pages = await run_controlled_extraction(
		extraction_context,
		monkeypatch,
		[ExtractedPage(1, "Persisted text", "native", confidence=0.95, ocr_used=True)],
	)

	page = pages[0]
	document = extraction_context[1]
	assert page.extracted_text == "Persisted text"
	assert page.page_number == 1
	assert page.extraction_method == "native"
	assert page.extraction_status == "completed"
	assert page.ocr_used is True
	assert page.extraction_confidence == 0.95
	assert page.error_summary is None
	assert extraction.status == "completed"
	assert document.processing_status == "completed"
	assert document.extraction_status == "completed"


@pytest.mark.asyncio
async def test_extraction_persists_multiple_pages_with_page_numbers_and_text(extraction_context, monkeypatch) -> None:
	from app.modules.extraction.extractors import ExtractedPage

	_, pages = await run_controlled_extraction(
		extraction_context,
		monkeypatch,
		[
			ExtractedPage(2, "Second page", "native"),
			ExtractedPage(1, "First page", "native"),
		],
	)

	assert [(page.page_number, page.extracted_text) for page in pages] == [
		(1, "First page"),
		(2, "Second page"),
	]


@pytest.mark.asyncio
async def test_extraction_persists_empty_text_as_empty_string(extraction_context, monkeypatch) -> None:
	from app.modules.extraction.extractors import ExtractedPage

	_, pages = await run_controlled_extraction(
		extraction_context,
		monkeypatch,
		[ExtractedPage(1, "", "native")],
	)

	assert pages[0].extracted_text == ""


@pytest.mark.asyncio
async def test_failed_pages_preserve_empty_text_status_and_error(extraction_context, monkeypatch) -> None:
	extraction, pages = await run_controlled_extraction(
		extraction_context,
		monkeypatch,
		[ExtractedPage(1, "", "ocr", status="failed", error_summary="OCR unavailable")],
	)

	page = pages[0]
	document = extraction_context[1]
	assert page.extracted_text == ""
	assert page.extraction_status == "failed"
	assert page.error_summary == "OCR unavailable"
	assert extraction.status == "failed"
	assert extraction.error_code == "page_extraction_failed"
	assert document.processing_status == "failed"
	assert document.extraction_status == "failed"


@pytest.mark.asyncio
async def test_extraction_failure_is_persisted_with_safe_status(extraction_context, monkeypatch) -> None:
	session, document, storage_root = extraction_context
	storage = LocalStorageProvider(storage_root)
	await storage.save(document.storage_key, b"content")

	class FailingExtractor:
		extractor_type = "tesseract"
		extractor_version = "test"

		def extract(self, content: bytes) -> list:
			raise CapabilityUnavailable("Tesseract is not installed")

	monkeypatch.setattr("app.modules.extraction.service.extractor_for", lambda _: FailingExtractor())
	extraction = await ExtractionService(session, storage).extract(document)

	assert extraction.status == "failed"
	assert extraction.error_code == "extraction_failed"
	assert extraction.error_summary == "Tesseract is not installed"
	assert document.processing_status == "failed"
	assert document.extraction_status == "failed"


@pytest.mark.asyncio
async def test_rerun_replaces_old_page_preview(extraction_context, monkeypatch) -> None:
	session, document, storage_root = extraction_context
	storage = LocalStorageProvider(storage_root)
	await storage.save(document.storage_key, b"content")
	extractor = ControlledExtractor([ExtractedPage(1, "first", "native")])
	monkeypatch.setattr("app.modules.extraction.service.extractor_for", lambda _: extractor)
	await ExtractionService(session, storage).extract(document)
	extractor.pages = [ExtractedPage(1, "second", "native")]
	await ExtractionService(session, storage).extract(document)
	persisted = list(await session.scalars(select(DocumentPage).where(DocumentPage.document_id == document.id)))
	assert [page.extracted_text for page in persisted] == ["second"]


def test_text_extractor_preserves_unicode() -> None:
	pages = TextExtractor().extract("සිංහල Tamil English".encode("utf-8"))
	assert pages[0].text == "සිංහල Tamil English"
	assert pages[0].page_number == 1


def test_csv_extractor_preserves_rows_and_columns() -> None:
	pages = CsvExtractor().extract(b"name,score\nAda,10\n")
	assert pages[0].text == "name\tscore\nAda\t10"


def test_docx_extractor_reads_paragraphs_and_tables() -> None:
	document = WordDocument()
	document.add_paragraph("Heading")
	table = document.add_table(rows=1, cols=2)
	table.cell(0, 0).text = "A"
	table.cell(0, 1).text = "B"
	output = BytesIO()
	document.save(output)
	pages = DocxExtractor().extract(output.getvalue())
	assert "Heading" in pages[0].text
	assert "A\tB" in pages[0].text


def test_pdf_extractor_handles_real_pdf_container() -> None:
	writer = PdfWriter()
	writer.add_blank_page(width=200, height=200)
	output = BytesIO()
	writer.write(output)
	pages = PdfExtractor().extract(output.getvalue())
	assert len(pages) == 1
	assert pages[0].page_number == 1
