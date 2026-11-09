from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.enums import FeedbackValue, InsightCategory


class IntelligenceRequestCreate(BaseModel):
	request_type: str = Field(min_length=1, max_length=64)
	input_text: str | None = None
	input_metadata: dict | None = None


class InsightCreate(BaseModel):
	analysis_run_id: UUID
	title: str = Field(min_length=1, max_length=200)
	description: str = Field(min_length=1)
	category: InsightCategory
	importance: int | None = Field(default=None, ge=0, le=100)
	confidence: float | None = Field(default=None, ge=0, le=1)
	uncertainty: float | None = Field(default=None, ge=0, le=1)


class ContextReferenceCreate(BaseModel):
	analysis_run_id: UUID
	reference_type: str = Field(min_length=1, max_length=32)
	reference_id: UUID


class FeedbackCreate(BaseModel):
	insight_id: UUID
	value: FeedbackValue
	correction: str | None = Field(default=None, max_length=5000)


class IntelligenceResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: UUID
	user_id: UUID
