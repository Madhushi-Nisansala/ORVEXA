from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SearchEntity(StrEnum):
	documents = "documents"
	tasks = "tasks"
	goals = "goals"
	insights = "insights"
	memories = "memories"


class SearchSort(StrEnum):
	relevance = "relevance"
	created_at = "created_at"
	updated_at = "updated_at"
	title = "title"


class SearchResult(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	title: str
	entity_type: SearchEntity
	summary: str
	navigation_ref: str
	category: str | None = None
	status: str | None = None
	created_at: datetime
	updated_at: datetime | None = None


class SearchGroup(BaseModel):
	items: list[SearchResult]
	total: int


class GlobalSearchResponse(BaseModel):
	query: str | None
	limit: int
	offset: int
	total: int
	groups: dict[str, SearchGroup]


class SearchParameters(BaseModel):
	q: str | None = Field(default=None, min_length=1, max_length=200)
	entities: list[SearchEntity] = Field(default_factory=lambda: list(SearchEntity))
	category: str | None = Field(default=None, min_length=1, max_length=64)
	status: str | None = Field(default=None, min_length=1, max_length=32)
	date_from: datetime | None = None
	date_to: datetime | None = None
	sort: SearchSort = SearchSort.relevance
	order: str = Field(default="desc", pattern="^(asc|desc)$")
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0, le=100000)

	@model_validator(mode="after")
	def validate_dates(self) -> "SearchParameters":
		if self.date_from and self.date_to and self.date_from > self.date_to:
			raise ValueError("date_from must be before or equal to date_to")
		return self
