from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.analysis_models import DocumentProcessingJob
from app.modules.documents.document_models import Document, DocumentPage
from app.modules.documents.storage import LocalStorageProvider, StorageError
from app.modules.extraction.extractors import CapabilityUnavailable, ExtractionError, extractor_for
from app.modules.extraction.models import DocumentExtraction


class ExtractionService:
	def __init__(self, session: AsyncSession, storage: LocalStorageProvider) -> None:
		self.session = session
		self.storage = storage

	async def extract(self, document: Document, job: DocumentProcessingJob | None = None) -> DocumentExtraction:
		now = datetime.now(timezone.utc)
		extractor = extractor_for(f".{document.document_type.lower().lstrip('.')}")
		extraction = DocumentExtraction(
			id=uuid4(),
			user_id=document.user_id,
			document_id=document.id,
			extractor_type=extractor.extractor_type,
			extractor_version=extractor.extractor_version,
			detected_document_type=document.document_type,
			processing_version=job.processing_version if job is not None else "stage2-v1",
			language_detection_status="not_run",
			status="processing",
			created_at=now,
		)
		self.session.add(extraction)
		document.processing_status = "processing"
		document.extraction_status = "processing"
		document.updated_at = now
		await self.session.flush()
		await self.session.execute(delete(DocumentPage).where(DocumentPage.document_id == document.id))
		try:
			content = await self.storage.read(document.storage_key)
			pages = extractor.extract(content)
		except StorageError as exc:
			return await self._persist_failure(document, extraction, "stored_document_unavailable", "Stored document is unavailable", now)
		except (CapabilityUnavailable, ExtractionError) as exc:
			return await self._persist_failure(document, extraction, "extraction_failed", _safe_error(str(exc), "Extraction failed"), now)

		for page in pages:
			self.session.add(DocumentPage(
				id=uuid4(), document_id=document.id, page_number=page.page_number,
				extracted_text=page.text,
				extraction_method=page.method,
				extraction_status=page.status,
				ocr_used=page.ocr_used,
				error_summary=page.error_summary,
				extraction_confidence=page.confidence, created_at=now,
			))
		failed_pages = [page for page in pages if page.status == "failed"]
		extraction.status = "failed" if pages and len(failed_pages) == len(pages) else ("partial" if failed_pages else "completed")
		if failed_pages:
			extraction.error_code = "page_extraction_failed"
			extraction.error_summary = "One or more pages could not be extracted"
		extraction.completed_at = datetime.now(timezone.utc)
		document.processing_status = "completed" if extraction.status != "failed" else "failed"
		document.extraction_status = extraction.status
		document.updated_at = datetime.now(timezone.utc)
		await self.session.commit()
		await self.session.refresh(extraction)
		return extraction

	async def _persist_failure(
		self,
		document: Document,
		extraction: DocumentExtraction,
		error_code: str,
		error_summary: str,
		now: datetime,
	) -> DocumentExtraction:
		extraction.status = "failed"
		extraction.error_code = error_code
		extraction.error_summary = error_summary
		extraction.completed_at = datetime.now(timezone.utc)
		document.processing_status = "failed"
		document.extraction_status = "failed"
		document.updated_at = now
		await self.session.commit()
		await self.session.refresh(extraction)
		return extraction

	async def latest_job(self, document_id: UUID) -> DocumentProcessingJob | None:
		return await self.session.scalar(
			select(DocumentProcessingJob)
			.where(DocumentProcessingJob.document_id == document_id)
			.order_by(DocumentProcessingJob.created_at.desc())
		)


def _safe_error(value: str, fallback: str) -> str:
	return " ".join(value.split())[:500] or fallback
