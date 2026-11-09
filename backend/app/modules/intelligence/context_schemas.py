from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContextType(StrEnum):
	user_provided = "USER_PROVIDED_CONTEXT"
	user_confirmed = "USER_CONFIRMED_CONTEXT"
	document_derived = "DOCUMENT_DERIVED_CONTEXT"
	interaction_derived = "INTERACTION_DERIVED_CONTEXT"
	temporary = "TEMPORARY_CONTEXT"
	unconfirmed = "UNCONFIRMED_CONTEXT"


class ConfirmationStatus(StrEnum):
	unconfirmed = "unconfirmed"
	confirmed = "confirmed"
	rejected = "rejected"


class ContextCreate(BaseModel):
	context_type: ContextType = ContextType.user_provided
	title: str | None = Field(default=None, min_length=1, max_length=200)
	category: str = Field(min_length=1, max_length=64)
	content: dict = Field(min_length=1)
	source_type: str = Field(default="user", min_length=1, max_length=32)
	source_reference: str | None = Field(default=None, max_length=500)
	evidence_reference: UUID | None = None
	confidence: str | None = Field(default=None, max_length=16)
	review_after: datetime | None = None
	expires_at: datetime | None = None
	retention_policy: str = Field(default="user_controlled", max_length=32)


class ContextUpdate(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=200)
	category: str | None = Field(default=None, min_length=1, max_length=64)
	content: dict | None = Field(default=None, min_length=1)
	review_after: datetime | None = None
	expires_at: datetime | None = None
	retention_policy: str | None = Field(default=None, max_length=32)


class ContextResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	context_type: str
	title: str
	category: str
	content: dict
	source_type: str
	source_reference: str | None
	evidence_reference: UUID | None
	confidence: str | None
	confirmation_status: str
	is_active: bool
	review_after: datetime | None
	expires_at: datetime | None
	retention_policy: str
	created_at: datetime
	updated_at: datetime
	deleted_at: datetime | None


class ContextPreferenceUpdate(BaseModel):
	persistent_memory_enabled: bool | None = None
	allow_document_derived_context: bool | None = None
	allow_interaction_derived_context: bool | None = None
	default_retention_days: int | None = Field(default=None, ge=1, le=3650)


class ContextPreferenceResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	user_id: UUID
	persistent_memory_enabled: bool
	allow_document_derived_context: bool
	allow_interaction_derived_context: bool
	default_retention_days: int | None
	updated_at: datetime


class InsightFeedbackCreate(BaseModel):
	value: str = Field(min_length=1, max_length=32)
	correction: str | None = Field(default=None, max_length=4000)


class InsightResponse(BaseModel):
	id: UUID
	title: str
	description: str
	category: str
	importance: int | None
	confidence: float | None
	uncertainty: float | None
	status: str
	evidence_source_ids: list[UUID]
	created_at: datetime


class InsightGenerationResponse(BaseModel):
	sufficient_information: bool
	limitation: str | None = None
	insight: InsightResponse | None = None
