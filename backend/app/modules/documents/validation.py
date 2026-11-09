from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass
from pathlib import PurePath
from urllib.parse import unquote


class DocumentValidationError(ValueError):
	pass


@dataclass(frozen=True)
class ValidatedDocument:
	filename: str
	extension: str
	media_type: str
	size: int
	sha256_hash: str
	content: bytes


_ALLOWED: dict[str, set[str]] = {
	".pdf": {"application/pdf"},
	".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/zip"},
	".txt": {"text/plain", "application/octet-stream"},
	".csv": {"text/csv", "application/csv", "application/vnd.ms-excel", "text/plain"},
	".png": {"image/png"},
	".jpg": {"image/jpeg"},
	".jpeg": {"image/jpeg"},
}


def _signature_matches(extension: str, content: bytes) -> bool:
	if extension == ".pdf":
		return content.startswith(b"%PDF-")
	if extension == ".docx":
		if not content.startswith(b"PK"):
			return False
		try:
			with zipfile.ZipFile(io.BytesIO(content)) as archive:
				names = set(archive.namelist())
				return {
					"[Content_Types].xml",
					"word/document.xml",
				}.issubset(names) and archive.testzip() is None
		except (zipfile.BadZipFile, OSError):
			return False
	if extension == ".png":
		return content.startswith(b"\x89PNG\r\n\x1a\n")
	if extension in {".jpg", ".jpeg"}:
		return content.startswith(b"\xff\xd8\xff")
	if extension in {".txt", ".csv"}:
		try:
			content.decode("utf-8")
		except UnicodeDecodeError:
			return False
		return b"\x00" not in content
	return True


def validate_document(filename: str | None, media_type: str | None, content: bytes, max_size: int) -> ValidatedDocument:
	if not filename or not content:
		raise DocumentValidationError("Document filename and content are required")
	filename = unquote(filename)
	if len(filename) > 255 or any(ord(character) < 32 or ord(character) == 127 for character in filename):
		raise DocumentValidationError("Document filename is invalid")
	if len(content) > max_size:
		raise DocumentValidationError("Document exceeds the maximum allowed size")
	if "/" in filename or "\\" in filename:
		raise DocumentValidationError("Document filename must not contain a path")
	safe_name = PurePath(filename).name
	extension = PurePath(safe_name).suffix.lower()
	if not safe_name or safe_name in {".", ".."} or safe_name != filename or extension not in _ALLOWED:
		raise DocumentValidationError("Unsupported document filename or format")
	supplied_type = (media_type or "").lower().split(";", 1)[0].strip()
	if not supplied_type:
		raise DocumentValidationError("Document media type is required")
	if supplied_type not in _ALLOWED[extension]:
		raise DocumentValidationError("Document media type does not match its extension")
	if not _signature_matches(extension, content):
		raise DocumentValidationError("Document signature does not match its extension")
	return ValidatedDocument(
		filename=safe_name,
		extension=extension,
		media_type=supplied_type or next(iter(_ALLOWED[extension])),
		size=len(content),
		sha256_hash=hashlib.sha256(content).hexdigest(),
		content=content,
	)
