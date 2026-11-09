from enum import StrEnum

from pydantic import BaseModel


class ErrorCode(StrEnum):
	not_found = "not_found"
	unauthorized = "unauthorized"
	forbidden = "forbidden"
	validation_error = "validation_error"
	conflict = "conflict"
	processing_failure = "processing_failure"
	internal_error = "internal_error"


class ErrorDetail(BaseModel):
	code: ErrorCode
	message: str


class ErrorResponse(BaseModel):
	error: ErrorDetail
