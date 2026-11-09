from pathlib import Path

import pytest

from app.modules.documents.storage import LocalStorageProvider, StorageError
from app.modules.documents.validation import DocumentValidationError, validate_document


def test_pdf_validation_checks_signature_and_hash() -> None:
	validated = validate_document("report.pdf", "application/pdf", b"%PDF-1.7\ncontent", 1024)
	assert validated.extension == ".pdf"
	assert len(validated.sha256_hash) == 64


def test_invalid_signature_is_rejected() -> None:
	with pytest.raises(DocumentValidationError):
		validate_document("report.pdf", "application/pdf", b"not a pdf", 1024)


def test_path_traversal_filename_is_rejected() -> None:
	with pytest.raises(DocumentValidationError):
		validate_document("../report.pdf", "application/pdf", b"%PDF-1.7", 1024)


def test_size_limit_is_enforced() -> None:
	with pytest.raises(DocumentValidationError):
		validate_document("note.txt", "text/plain", b"12345", 4)


@pytest.mark.asyncio
async def test_local_storage_rejects_traversal_and_keeps_keys_private(tmp_path: Path) -> None:
	storage = LocalStorageProvider(tmp_path)
	await storage.save("aa/file.txt", b"content")
	assert await storage.read("aa/file.txt") == b"content"
	with pytest.raises(StorageError):
		await storage.read("../file.txt")
	assert "file.txt" not in storage.key_for(__import__("uuid").uuid4(), ".pdf")