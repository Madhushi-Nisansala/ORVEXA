from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EvidenceSource(Base):
	__tablename__ = "evidence_sources"
	__table_args__ = (
		Index("ix_evidence_sources_user_id", "user_id"),
		CheckConstraint("document_id IS NOT NULL OR analysis_run_id IS NOT NULL", name="ck_evidence_source_parent"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	document_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("documents.id", ondelete="RESTRICT"))
	analysis_run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("analysis_runs.id", ondelete="RESTRICT"))
	source_type: Mapped[str] = mapped_column(String(32), nullable=False)
	source_reference: Mapped[str] = mapped_column(String(500), nullable=False)
	page_number: Mapped[int | None] = mapped_column(Integer)
	section_reference: Mapped[str | None] = mapped_column(String(200))
	excerpt: Mapped[str | None] = mapped_column(Text)
	verification_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unverified", server_default="unverified")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
