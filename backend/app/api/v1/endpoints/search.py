from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.modules.search.schemas import GlobalSearchResponse, SearchEntity, SearchParameters, SearchSort
from app.modules.search.service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=GlobalSearchResponse)
async def global_search(
	q: str | None = Query(default=None, min_length=1, max_length=200),
	entities: list[SearchEntity] = Query(default_factory=lambda: list(SearchEntity)),
	category: str | None = Query(default=None, min_length=1, max_length=64),
	status: str | None = Query(default=None, min_length=1, max_length=32),
	date_from: datetime | None = None,
	date_to: datetime | None = None,
	sort: SearchSort = SearchSort.relevance,
	order: str = Query(default="desc", pattern="^(asc|desc)$"),
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0, le=100000),
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> GlobalSearchResponse:
	if date_from and date_to and date_from > date_to:
		raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail="date_from must be before or equal to date_to")
	parameters = SearchParameters(
		q=q,
		entities=entities,
		category=category,
		status=status,
		date_from=date_from,
		date_to=date_to,
		sort=sort,
		order=order,
		limit=limit,
		offset=offset,
	)
	return await SearchService(db).search(user.id, parameters)
