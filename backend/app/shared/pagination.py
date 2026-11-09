from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
	limit: int = Field(default=50, ge=1, le=100)
	offset: int = Field(default=0, ge=0)


class Page[T](BaseModel):
	items: list[T]
	limit: int
	offset: int
	total: int = Field(ge=0)
