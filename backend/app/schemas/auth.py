from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

SUPPORTED_LANGUAGES = {"en", "si", "ta"}


class UserCreate(BaseModel):
	email: EmailStr
	password: str = Field(min_length=8, max_length=1024)
	full_name: str | None = Field(default=None, max_length=200)
	preferred_language: str = Field(default="en", min_length=2, max_length=2)

	@field_validator("preferred_language")
	@classmethod
	def validate_language(cls, value: str) -> str:
		value = value.lower()
		if value not in SUPPORTED_LANGUAGES:
			raise ValueError("Unsupported language")
		return value


class LoginRequest(BaseModel):
	email: EmailStr
	password: str = Field(min_length=1, max_length=1024)
	device_name: str | None = Field(default=None, max_length=200)


class RefreshRequest(BaseModel):
	refresh_token: str = Field(min_length=20, max_length=512)


class UserResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	email: EmailStr
	full_name: str | None
	preferred_language: str
	is_active: bool
	is_verified: bool
	created_at: datetime
	updated_at: datetime
	last_login_at: datetime | None
	roles: list[str]


class TokenResponse(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str = "bearer"
	expires_in: int
	user: UserResponse


class ProfileUpdate(BaseModel):
	full_name: str | None = Field(default=None, max_length=200)
	preferred_language: str | None = Field(default=None, min_length=2, max_length=2)

	@field_validator("preferred_language")
	@classmethod
	def validate_language(cls, value: str | None) -> str | None:
		if value is not None and value.lower() not in SUPPORTED_LANGUAGES:
			raise ValueError("Unsupported language")
		return value.lower() if value else value
