from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractionResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: UUID
	document_id: UUID
	extractor_type: str
	extractor_version: str
	detected_document_type: str | None
	processing_version: str
	language_detection_status: str
	detected_language: str | None
	status: str
	error_code: str | None
	error_summary: str | None
	created_at: datetime
	completed_at: datetime | None


class ExtractedPageResponse(BaseModel):
	page_number: int
	text: str
	extraction_method: str
	extraction_status: str
	ocr_used: bool
	error_summary: str | None
	extraction_confidence: float | None
