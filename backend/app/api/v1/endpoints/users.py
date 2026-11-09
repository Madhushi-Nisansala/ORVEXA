from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.security import utc_now
from app.database.models import User
from app.database.session import get_db
from app.schemas.auth import ProfileUpdate, UserResponse
from app.services.auth import user_response_data

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)) -> UserResponse:
	return UserResponse.model_validate(user_response_data(user))


@router.patch("/me", response_model=UserResponse)
async def update_profile(
	payload: ProfileUpdate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> UserResponse:
	changes = payload.model_dump(exclude_unset=True)
	if "full_name" in changes:
		user.full_name = changes["full_name"].strip() if changes["full_name"] else None
	if "preferred_language" in changes and changes["preferred_language"] is not None:
		user.preferred_language = changes["preferred_language"]
	user.updated_at = utc_now()
	await db.commit()
	await db.refresh(user)
	return UserResponse.model_validate(user_response_data(user))
