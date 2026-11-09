from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, JSON, String, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class IntelligenceRequest(Base):
	__tablename__ = "intelligence_requests"
	__table_args__ = (Index("ix_intelligence_requests_user_id", "user_id"),)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	request_type: Mapped[str] = mapped_column(String(64), nullable=False)
	input_text: Mapped[str | None] = mapped_column(Text)
	input_metadata: Mapped[dict | None] = mapped_column(JSON)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", server_default="pending")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class DocumentAnalysis(Base):
	__tablename__ = "document_analyses"
	__table_args__ = (
		UniqueConstraint("document_id", "version", name="uq_document_analyses_document_version"),
		Index("ix_document_analyses_user_id", "user_id"),
		Index("ix_document_analyses_document_id", "document_id"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("documents.id", ondelete="RESTRICT"), nullable=False)
	extraction_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("document_extractions.id", ondelete="RESTRICT"), nullable=False)
	version: Mapped[int] = mapped_column(nullable=False)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", server_default="pending")
	provider_identifier: Mapped[str | None] = mapped_column(String(128))
	model_name: Mapped[str | None] = mapped_column(String(128))
	result: Mapped[dict | None] = mapped_column(JSON)
	error_code: Mapped[str | None] = mapped_column(String(64))
	error_summary: Mapped[str | None] = mapped_column(String(500))
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DocumentInsight(Base):
	__tablename__ = "document_insights"
	__table_args__ = (
		UniqueConstraint("analysis_id", "title", name="uq_document_insights_analysis_title"),
		Index("ix_document_insights_user_id", "user_id"),
		Index("ix_document_insights_document_id", "document_id"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
	analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("document_analyses.id", ondelete="CASCADE"), nullable=False)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[str] = mapped_column(Text, nullable=False)
	category: Mapped[str] = mapped_column(String(32), nullable=False)
	importance: Mapped[int | None] = mapped_column()
	confidence: Mapped[float | None] = mapped_column()
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", server_default="active")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class AnalysisRun(Base):
	__tablename__ = "analysis_runs"
	__table_args__ = (
		Index("ix_analysis_runs_user_id", "user_id"),
		Index("ix_analysis_runs_request_id", "request_id"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	request_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("intelligence_requests.id", ondelete="RESTRICT"), nullable=False)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", server_default="pending")
	provider_identifier: Mapped[str | None] = mapped_column(String(128))
	started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	error_code: Mapped[str | None] = mapped_column(String(64))
	error_summary: Mapped[str | None] = mapped_column(String(500))


class IntelligenceInsight(Base):
	__tablename__ = "intelligence_insights"
	__table_args__ = (
		Index("ix_intelligence_insights_user_id", "user_id"),
		Index("ix_intelligence_insights_analysis_run_id", "analysis_run_id"),
		Index("ix_intelligence_insights_search_scope", "user_id", "category", "status", "created_at"),
		CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="ck_insights_confidence_range"),
		CheckConstraint("uncertainty IS NULL OR (uncertainty >= 0 AND uncertainty <= 1)", name="ck_insights_uncertainty_range"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	analysis_run_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("analysis_runs.id", ondelete="RESTRICT"), nullable=False)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[str] = mapped_column(Text, nullable=False)
	category: Mapped[str] = mapped_column(String(32), nullable=False)
	importance: Mapped[int | None] = mapped_column()
	confidence: Mapped[float | None] = mapped_column()
	uncertainty: Mapped[float | None] = mapped_column()
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", server_default="active")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ContextReference(Base):
	__tablename__ = "context_references"
	__table_args__ = (Index("ix_context_references_user_id", "user_id"),)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	analysis_run_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("analysis_runs.id", ondelete="RESTRICT"), nullable=False)
	reference_type: Mapped[str] = mapped_column(String(32), nullable=False)
	reference_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class UserFeedback(Base):
	__tablename__ = "user_feedback"
	__table_args__ = (Index("ix_user_feedback_user_id", "user_id"),)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	insight_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("intelligence_insights.id", ondelete="RESTRICT"), nullable=False)
	value: Mapped[str] = mapped_column(String(32), nullable=False)
	correction: Mapped[str | None] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
