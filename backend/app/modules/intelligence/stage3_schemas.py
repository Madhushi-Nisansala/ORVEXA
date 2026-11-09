from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InformationClassification(StrEnum):
	source_fact = "SOURCE_FACT"
	source_claim = "SOURCE_CLAIM"
	inference = "INFERENCE"
	assumption = "ASSUMPTION"
	unknown = "UNKNOWN"
	conflicting_information = "CONFLICTING_INFORMATION"


class AnalysisStatus(StrEnum):
	pending = "pending"
	processing = "processing"
	completed = "completed"
	partial = "partial"
	failed = "failed"
	provider_unavailable = "provider_unavailable"


class EvidenceValidationStatus(StrEnum):
	pending = "pending"
	validated = "validated"
	unsupported = "unsupported"
	invalid = "invalid"


class ConfidenceLevel(StrEnum):
	high = "high"
	medium = "medium"
	low = "low"
	unknown = "unknown"


class EvidenceReference(BaseModel):
	model_config = ConfigDict(extra="forbid")

	document_id: UUID
	extraction_id: UUID
	page_number: int = Field(ge=1)
	source_text: str = Field(min_length=1, max_length=4000)
	start_offset: int | None = Field(default=None, ge=0)
	end_offset: int | None = Field(default=None, ge=0)
	section_reference: str | None = Field(default=None, max_length=200)
	extraction_method: str | None = Field(default=None, max_length=64)
	validation_status: EvidenceValidationStatus = EvidenceValidationStatus.pending

	@model_validator(mode="after")
	def validate_offsets(self) -> "EvidenceReference":
		if self.start_offset is not None and self.end_offset is not None and self.end_offset < self.start_offset:
			raise ValueError("Evidence end offset must not precede its start offset")
		return self


class ClassifiedItem(BaseModel):
	model_config = ConfigDict(extra="forbid")

	classification: InformationClassification
	confidence: float | None = Field(default=None, ge=0, le=1)
	confidence_level: ConfidenceLevel = ConfidenceLevel.unknown
	uncertainty: str | None = Field(default=None, max_length=500)
	evidence: list[EvidenceReference] = Field(min_length=1, max_length=20)


class DocumentClassification(BaseModel):
	model_config = ConfigDict(extra="forbid")

	primary_type: str = Field(min_length=1, max_length=64)
	secondary_type: str | None = Field(default=None, max_length=64)
	confidence: float | None = Field(default=None, ge=0, le=1)
	explanation: str = Field(max_length=1000)
	evidence: list[EvidenceReference] = Field(default_factory=list, max_length=20)


class Fact(ClassifiedItem):
	fact_type: str = Field(min_length=1, max_length=64)
	value: str = Field(min_length=1, max_length=2000)
	original_value: str | None = Field(default=None, max_length=2000)
	validation_status: str = Field(default="unverified", max_length=32)


class Entity(ClassifiedItem):
	entity_type: str = Field(min_length=1, max_length=64)
	name: str = Field(min_length=1, max_length=500)


class DateReference(ClassifiedItem):
	date_type: str = Field(min_length=1, max_length=64)
	original_expression: str = Field(min_length=1, max_length=300)
	normalized_date: date | None = None
	is_ambiguous: bool = False


class Requirement(ClassifiedItem):
	description: str = Field(min_length=1, max_length=2000)
	responsible_party: str | None = Field(default=None, max_length=500)
	triggering_condition: str | None = Field(default=None, max_length=1000)
	due_date: DateReference | None = None


class Obligation(ClassifiedItem):
	description: str = Field(min_length=1, max_length=2000)
	responsible_party: str | None = Field(default=None, max_length=500)
	triggering_condition: str | None = Field(default=None, max_length=1000)
	due_date: DateReference | None = None


class FinancialItem(ClassifiedItem):
	financial_type: str = Field(min_length=1, max_length=64)
	original_amount: str = Field(min_length=1, max_length=200)
	currency: str | None = Field(default=None, max_length=16)
	context: str | None = Field(default=None, max_length=1000)


class Risk(ClassifiedItem):
	category: str = Field(min_length=1, max_length=64)
	description: str = Field(min_length=1, max_length=2000)
	severity: str = Field(default="low", max_length=16)
	explanation: str = Field(max_length=1000)
	suggested_verification: str | None = Field(default=None, max_length=1000)


class AnalysisResult(BaseModel):
	model_config = ConfigDict(extra="forbid")

	classification: DocumentClassification
	facts: list[Fact] = Field(default_factory=list, max_length=500)
	entities: list[Entity] = Field(default_factory=list, max_length=500)
	dates: list[DateReference] = Field(default_factory=list, max_length=200)
	requirements: list[Requirement] = Field(default_factory=list, max_length=200)
	obligations: list[Obligation] = Field(default_factory=list, max_length=200)
	financial_information: list[FinancialItem] = Field(default_factory=list, max_length=200)
	risks: list[Risk] = Field(default_factory=list, max_length=200)
	executive_summary: str | None = Field(default=None, max_length=5000)
	key_points: list[str] = Field(default_factory=list, max_length=100)
	topics: list[str] = Field(default_factory=list, max_length=100)
	action_items: list[str] = Field(default_factory=list, max_length=100)
	opportunities: list[str] = Field(default_factory=list, max_length=100)
	recommendations: list[str] = Field(default_factory=list, max_length=100)
	coverage_start_page: int | None = Field(default=None, ge=1)
	coverage_end_page: int | None = Field(default=None, ge=1)
	coverage_complete: bool = False
	unknowns: list[str] = Field(default_factory=list, max_length=100)
	conflicts: list[str] = Field(default_factory=list, max_length=100)

	@model_validator(mode="after")
	def validate_coverage(self) -> "AnalysisResult":
		if self.coverage_start_page and self.coverage_end_page and self.coverage_end_page < self.coverage_start_page:
			raise ValueError("Analysis coverage end page must not precede its start page")
		return self


class AnalysisResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	document_id: UUID
	extraction_id: UUID
	version: int
	status: AnalysisStatus
	provider_identifier: str | None
	model_name: str | None
	error_code: str | None
	error_summary: str | None
	result: AnalysisResult | None
	created_at: datetime
	completed_at: datetime | None


class AnalysisRequestResponse(BaseModel):
	analysis_id: UUID
	status: AnalysisStatus
	version: int


class EvidenceCollectionResponse(BaseModel):
	items: list[EvidenceReference]
	total: int


class AnalysisItemsResponse(BaseModel):
	items: list[dict]
	total: int


class InsightResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	document_id: UUID
	analysis_id: UUID
	title: str
	description: str
	category: str
	importance: int | None
	confidence: float | None
	status: str
	created_at: datetime


class InsightListResponse(BaseModel):
	items: list[InsightResponse]
	total: int
