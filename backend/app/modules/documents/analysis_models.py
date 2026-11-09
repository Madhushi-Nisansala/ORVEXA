from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class DocumentProcessingJob(Base):
	__tablename__ = 'document_processing_jobs'
	__table_args__ = (Index('ix_document_processing_jobs_document_id', 'document_id'),)
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
	job_type: Mapped[str] = mapped_column(String(32), nullable=False)
	status: Mapped[str] = mapped_column(String(32), default='queued', nullable=False)
	attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
	max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
	available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	error_message: Mapped[str | None] = mapped_column(Text)
	claim_token: Mapped[str | None] = mapped_column(String(64), unique=True)
	claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	processing_version: Mapped[str] = mapped_column(String(32), default='stage2-v1', nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class Analysis(Base):
	__tablename__ = 'analyses'
	__table_args__ = (Index('ix_analyses_user_id', 'user_id'), Index('ix_analyses_document_id', 'document_id'))
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
	document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
	provider: Mapped[str] = mapped_column(String(64), nullable=False)
	model_name: Mapped[str | None] = mapped_column(String(128))
	status: Mapped[str] = mapped_column(String(32), default='not_configured', nullable=False)
	summary: Mapped[dict | None] = mapped_column(JSON)
	category: Mapped[str | None] = mapped_column(String(64))
	detected_language: Mapped[str | None] = mapped_column(String(16))
	confidence: Mapped[float | None] = mapped_column()
	error_message: Mapped[str | None] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class ExtractedFact(Base):
	__tablename__ = 'extracted_facts'
	__table_args__ = (Index('ix_extracted_facts_analysis_id', 'analysis_id'),)
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False)
	fact_type: Mapped[str] = mapped_column(String(64), nullable=False)
	fact_value: Mapped[dict] = mapped_column(JSON, nullable=False)
	source_page: Mapped[int | None] = mapped_column(Integer)
	evidence_text: Mapped[str | None] = mapped_column(Text)
	confidence: Mapped[float | None] = mapped_column()
	verification_status: Mapped[str] = mapped_column(String(32), default='unverified', nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class ActionPlan(Base):
	__tablename__ = 'action_plans'
	__table_args__ = (Index('ix_action_plans_user_id', 'user_id'),)
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
	analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[str] = mapped_column(Text, nullable=False)
	status: Mapped[str] = mapped_column(String(32), default='proposed', nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class Action(Base):
	__tablename__ = 'actions'
	__table_args__ = (Index('ix_actions_user_id', 'user_id'), Index('ix_actions_action_plan_id', 'action_plan_id'))
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
	analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False)
	action_plan_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('action_plans.id', ondelete='CASCADE'), nullable=False)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[str] = mapped_column(Text, nullable=False)
	priority: Mapped[str] = mapped_column(String(16), default='medium', nullable=False)
	due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	status: Mapped[str] = mapped_column(String(32), default='proposed', nullable=False)
	evidence_reference: Mapped[dict | None] = mapped_column(JSON)
	confidence: Mapped[float | None] = mapped_column()
	approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
