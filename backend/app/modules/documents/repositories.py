from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.analysis_models import DocumentProcessingJob
from app.modules.documents.document_models import Document


class DocumentRepository:
	def __init__(self, session: AsyncSession) -> None:
		self.session = session

	async def get_owned(self, document_id: UUID, user_id: UUID) -> Document | None:
		return await self.session.scalar(
			select(Document).where(
				Document.id == document_id,
				Document.user_id == user_id,
				Document.deleted_at.is_(None),
			)
		)

	async def list_owned(self, user_id: UUID, limit: int, offset: int) -> tuple[list[Document], int]:
		base = select(Document).where(Document.user_id == user_id, Document.deleted_at.is_(None))
		total = await self.session.scalar(select(func.count()).select_from(base.subquery()))
		rows = await self.session.scalars(
			base.order_by(Document.created_at.desc()).limit(limit).offset(offset)
		)
		return list(rows), int(total or 0)

	async def find_duplicate(self, user_id: UUID, sha256_hash: str) -> Document | None:
		return await self.session.scalar(
			select(Document).where(
				Document.user_id == user_id,
				Document.sha256_hash == sha256_hash,
				Document.deleted_at.is_(None),
			)
		)

	async def latest_job(self, document_id: UUID) -> DocumentProcessingJob | None:
		return await self.session.scalar(
			select(DocumentProcessingJob)
			.where(DocumentProcessingJob.document_id == document_id)
			.order_by(DocumentProcessingJob.created_at.desc())
		)

	async def active_job(self, document_id: UUID) -> DocumentProcessingJob | None:
		return await self.session.scalar(
			select(DocumentProcessingJob)
			.where(
				DocumentProcessingJob.document_id == document_id,
				DocumentProcessingJob.status.in_(("queued", "processing", "retry_pending")),
			)
			.order_by(DocumentProcessingJob.created_at.desc())
		)
