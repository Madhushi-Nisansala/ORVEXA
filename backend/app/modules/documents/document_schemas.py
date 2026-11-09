from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: UUID
	original_filename: str
	mime_type: str
	file_size: int
	sha256_hash: str
	document_type: str
	detected_language: str | None
	processing_status: str
	extraction_status: str
	created_at: datetime
	updated_at: datetime
	archived_at: datetime | None


class DocumentSearchResponse(BaseModel):
	items: list[DocumentResponse]


class DocumentListResponse(BaseModel):
	items: list[DocumentResponse]
	limit: int = Field(ge=1)
	offset: int = Field(ge=0)
	total: int = Field(ge=0)


class ProcessingJobResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: UUID
	document_id: UUID
	status: str
	attempts: int
	max_attempts: int
	available_at: datetime
	error_message: str | None
	created_at: datetime
