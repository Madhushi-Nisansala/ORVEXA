from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.shared.enums import VerificationStatus


class EvidenceSourceCreate(BaseModel):
	document_id: UUID | None = None
	analysis_run_id: UUID | None = None
	source_type: str = Field(min_length=1, max_length=32)
	source_reference: str = Field(min_length=1, max_length=500)
	page_number: int | None = Field(default=None, ge=1)
	section_reference: str | None = Field(default=None, max_length=200)
	excerpt: str | None = None
	verification_status: VerificationStatus = VerificationStatus.unverified

	@model_validator(mode="after")
	def require_parent(self) -> "EvidenceSourceCreate":
		if self.document_id is None and self.analysis_run_id is None:
			raise ValueError("An evidence source must reference a document or analysis run")
		return self
