from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.modules.documents.analysis_models import DocumentProcessingJob
from app.modules.documents.document_models import Document
from app.modules.documents.repositories import DocumentRepository
from app.modules.documents.storage import LocalStorageProvider
from app.modules.documents.validation import validate_document


class DocumentNotFoundError(LookupError):
	pass


class DuplicateDocumentError(ValueError):
	def __init__(self, document: Document) -> None:
		self.document = document
		super().__init__("Document already exists")


class DocumentService:
	def __init__(self, session: AsyncSession, settings: Settings) -> None:
		self.session = session
		self.settings = settings
		self.repository = DocumentRepository(session)
		self.storage = LocalStorageProvider(settings.document_storage_root)

	async def create_upload(self, user_id: UUID, filename: str | None, media_type: str | None, content: bytes) -> Document:
		validated = validate_document(filename, media_type, content, self.settings.document_max_file_size_bytes)
		duplicate = await self.repository.find_duplicate(user_id, validated.sha256_hash)
		if duplicate is not None:
			raise DuplicateDocumentError(duplicate)
		document_id = uuid4()
		now = datetime.now(timezone.utc)
		storage_key = self.storage.key_for(document_id, validated.extension)
		document = Document(
			id=document_id,
			user_id=user_id,
			original_filename=validated.filename,
			storage_key=storage_key,
			mime_type=validated.media_type,
			file_size=validated.size,
			sha256_hash=validated.sha256_hash,
			document_type=validated.extension.removeprefix("."),
			processing_status="queued",
			extraction_status="pending",
			created_at=now,
			updated_at=now,
		)
		await self.storage.save(storage_key, validated.content)
		self.session.add(document)
		self.session.add(DocumentProcessingJob(
			id=uuid4(),
			document_id=document_id,
			job_type="extract",
			status="queued",
			attempts=0,
			max_attempts=self.settings.extraction_max_attempts,
			available_at=now,
			processing_version=self.settings.extraction_processing_version,
			created_at=now,
		))
		try:
			await self.session.commit()
		except Exception:
			await self.session.rollback()
			await self.storage.delete(storage_key)
			raise
		await self.session.refresh(document)
		return document

	async def get_owned(self, document_id: UUID, user_id: UUID) -> Document:
		document = await self.repository.get_owned(document_id, user_id)
		if document is None:
			raise DocumentNotFoundError
		return document

	async def archive(self, document_id: UUID, user_id: UUID) -> Document:
		document = await self.get_owned(document_id, user_id)
		document.archived_at = datetime.now(timezone.utc)
		document.updated_at = datetime.now(timezone.utc)
		await self.session.commit()
		await self.session.refresh(document)
		return document

	async def retry(self, document_id: UUID, user_id: UUID) -> DocumentProcessingJob:
		document = await self.get_owned(document_id, user_id)
		now = datetime.now(timezone.utc)
		active = await self.repository.active_job(document.id)
		if active is not None:
			return active
		latest = await self.repository.latest_job(document.id)
		if latest is not None and latest.status == "failed":
			latest.status = "queued"
			latest.attempts = 0
			latest.error_message = None
			latest.available_at = now
			latest.started_at = None
			latest.completed_at = None
			latest.claimed_at = None
			latest.claim_token = None
			document.processing_status = "queued"
			document.extraction_status = "pending"
			document.updated_at = now
			await self.session.commit()
			await self.session.refresh(latest)
			return latest
		job = DocumentProcessingJob(
			id=uuid4(), document_id=document.id, job_type="extract", status="queued", attempts=0,
			max_attempts=self.settings.extraction_max_attempts, available_at=now,
			processing_version=self.settings.extraction_processing_version, created_at=now,
		)
		document.processing_status = "queued"
		document.updated_at = now
		self.session.add(job)
		await self.session.commit()
		await self.session.refresh(job)
		return job

	async def enqueue_extraction(self, document_id: UUID, user_id: UUID) -> DocumentProcessingJob:
		document = await self.get_owned(document_id, user_id)
		active = await self.repository.active_job(document.id)
		if active is not None:
			return active
		latest = await self.repository.latest_job(document.id)
		if latest is not None and latest.status == "completed":
			return latest
		return await self.retry(document.id, user_id)

	async def delete(self, document_id: UUID, user_id: UUID) -> None:
		document = await self.get_owned(document_id, user_id)
		storage_key = document.storage_key
		document.deleted_at = datetime.now(timezone.utc)
		document.updated_at = datetime.now(timezone.utc)
		await self.session.commit()
		await self.storage.delete(storage_key)
