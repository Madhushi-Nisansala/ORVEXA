from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Document(Base):
	__tablename__ = 'documents'
	__table_args__ = (
		Index('ix_documents_user_id', 'user_id'),
		Index('ix_documents_sha256_hash', 'sha256_hash'),
		Index('ix_documents_user_archived_at', 'user_id', 'archived_at'),
		Index('ix_documents_search_scope', 'user_id', 'deleted_at', 'archived_at', 'created_at'),
	)
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
	original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
	storage_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
	mime_type: Mapped[str] = mapped_column(String(127), nullable=False)
	file_size: Mapped[int] = mapped_column(Integer, nullable=False)
	sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
	document_type: Mapped[str] = mapped_column(String(32), nullable=False)
	detected_language: Mapped[str | None] = mapped_column(String(16))
	processing_status: Mapped[str] = mapped_column(String(32), default='uploaded', nullable=False)
	extraction_status: Mapped[str] = mapped_column(String(32), default='pending', nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	pages: Mapped[list['DocumentPage']] = relationship(back_populates='document', cascade='all, delete-orphan')

class DocumentPage(Base):
	__tablename__ = 'document_pages'
	__table_args__ = (Index('ix_document_pages_document_id', 'document_id'),)
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
	page_number: Mapped[int] = mapped_column(Integer, nullable=False)
	extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
	extraction_method: Mapped[str] = mapped_column(String(32), nullable=False)
	extraction_status: Mapped[str] = mapped_column(String(32), nullable=False, default='completed')
	ocr_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	error_summary: Mapped[str | None] = mapped_column(String(500))
	extraction_confidence: Mapped[float | None] = mapped_column()
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	document: Mapped[Document] = relationship(back_populates='pages')
