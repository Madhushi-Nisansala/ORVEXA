from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DocumentExtraction(Base):
	__tablename__ = "document_extractions"
	__table_args__ = (
		Index("ix_document_extractions_user_id", "user_id"),
		Index("ix_document_extractions_document_id", "document_id"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("documents.id", ondelete="RESTRICT"), nullable=False)
	extractor_type: Mapped[str] = mapped_column(String(64), nullable=False)
	extractor_version: Mapped[str] = mapped_column(String(32), nullable=False)
	detected_language: Mapped[str | None] = mapped_column(String(16))
	detected_document_type: Mapped[str | None] = mapped_column(String(32))
	processing_version: Mapped[str] = mapped_column(String(32), nullable=False, default="stage2-v1")
	language_detection_status: Mapped[str] = mapped_column(String(32), nullable=False, default="not_run")
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="processing", server_default="processing")
	error_code: Mapped[str | None] = mapped_column(String(64))
	error_summary: Mapped[str | None] = mapped_column(String(500))
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
