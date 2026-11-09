from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserContext(Base):
	__tablename__ = "user_context"
	__table_args__ = (
		Index("ix_user_context_user_active", "user_id", "is_active"),
		Index("ix_user_context_user_category", "user_id", "category"),
		Index("ix_user_context_review_after", "review_after"),
		Index("ix_user_context_search_scope", "user_id", "is_active", "category", "created_at"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(
		Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
	)
	context_type: Mapped[str] = mapped_column(String(32), nullable=False)
	title: Mapped[str] = mapped_column(String(200), nullable=False, default="Untitled memory", server_default="Untitled memory")
	category: Mapped[str] = mapped_column(String(64), nullable=False)
	content: Mapped[dict] = mapped_column(JSON, nullable=False)
	source_type: Mapped[str] = mapped_column(String(32), nullable=False)
	source_reference: Mapped[str | None] = mapped_column(String(500))
	evidence_reference: Mapped[uuid.UUID | None] = mapped_column(
		Uuid, ForeignKey("evidence_sources.id", ondelete="RESTRICT")
	)
	confidence: Mapped[str | None] = mapped_column(String(16))
	confirmation_status: Mapped[str] = mapped_column(
		String(16), nullable=False, default="unconfirmed", server_default="unconfirmed"
	)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
	review_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	retention_policy: Mapped[str] = mapped_column(
		String(32), nullable=False, default="user_controlled", server_default="user_controlled"
	)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
	)
	deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ContextPreference(Base):
	__tablename__ = "context_preferences"

	user_id: Mapped[uuid.UUID] = mapped_column(
		Uuid, ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
	)
	persistent_memory_enabled: Mapped[bool] = mapped_column(
		Boolean, nullable=False, default=False, server_default="false"
	)
	allow_document_derived_context: Mapped[bool] = mapped_column(
		Boolean, nullable=False, default=False, server_default="false"
	)
	allow_interaction_derived_context: Mapped[bool] = mapped_column(
		Boolean, nullable=False, default=False, server_default="false"
	)
	default_retention_days: Mapped[int | None] = mapped_column()
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
	)


class InsightEvidence(Base):
	__tablename__ = "insight_evidence"
	__table_args__ = (
		Index("ix_insight_evidence_user_id", "user_id"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(
		Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
	)
	insight_id: Mapped[uuid.UUID] = mapped_column(
		Uuid, ForeignKey("intelligence_insights.id", ondelete="RESTRICT"), nullable=False
	)
	evidence_source_id: Mapped[uuid.UUID] = mapped_column(
		Uuid, ForeignKey("evidence_sources.id", ondelete="RESTRICT"), nullable=False
	)
	relation: Mapped[str] = mapped_column(String(32), nullable=False, default="supports", server_default="supports")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
