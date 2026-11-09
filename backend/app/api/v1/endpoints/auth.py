from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.dependencies import get_current_user
from app.core.config import get_settings
from app.core.rate_limit import enforce_auth_rate_limit
from app.core.security import hash_password, hash_refresh_token, utc_now, verify_password
from app.database.models import RefreshToken, User
from app.database.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth import (
	assign_default_role,
	issue_token_pair,
	rotate_refresh_token,
	user_response_data,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
_INVALID_PASSWORD_HASH = hash_password("ORVEXA-invalid-credential-check")


def invalid_credentials() -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Invalid email or password",
		headers={"WWW-Authenticate": "Bearer"},
	)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
	payload: UserCreate,
	request: Request,
	db: AsyncSession = Depends(get_db),
) -> UserResponse:
	enforce_auth_rate_limit(f"register:{request.client.host if request.client else 'unknown'}")
	email = str(payload.email).strip().lower()
	existing = await db.scalar(select(User).where(User.email == email))
	if existing is not None:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unable to create account")
	now = utc_now()
	user = User(
		email=email,
		password_hash=hash_password(payload.password),
		full_name=payload.full_name.strip() if payload.full_name else None,
		preferred_language=payload.preferred_language,
		is_active=True,
		is_verified=False,
		created_at=now,
		updated_at=now,
	)
	await assign_default_role(db, user)
	db.add(user)
	try:
		await db.commit()
	except IntegrityError as exc:
		await db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unable to create account") from exc
	await db.refresh(user, attribute_names=["roles"])
	return UserResponse.model_validate(user_response_data(user))


@router.post("/login", response_model=TokenResponse)
async def login(
	payload: LoginRequest,
	request: Request,
	db: AsyncSession = Depends(get_db),
) -> TokenResponse:
	enforce_auth_rate_limit(f"login:{request.client.host if request.client else 'unknown'}")
	email = str(payload.email).strip().lower()
	user = await db.scalar(select(User).options(selectinload(User.roles)).where(User.email == email))
	if user is None:
		verify_password(payload.password, _INVALID_PASSWORD_HASH)
		raise invalid_credentials()
	if not verify_password(payload.password, user.password_hash) or not user.is_active:
		raise invalid_credentials()
	user.last_login_at = utc_now()
	user.updated_at = utc_now()
	access, refresh = await issue_token_pair(db, user, payload.device_name)
	await db.commit()
	settings = get_settings()
	return TokenResponse(
		access_token=access,
		refresh_token=refresh,
		expires_in=settings.access_token_expire_minutes * 60,
		user=UserResponse.model_validate(user_response_data(user)),
	)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
	result = await rotate_refresh_token(db, payload.refresh_token)
	if result is None:
		await db.commit()
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
	user, access, refresh_token = result
	await db.commit()
	settings = get_settings()
	return TokenResponse(
		access_token=access,
		refresh_token=refresh_token,
		expires_in=settings.access_token_expire_minutes * 60,
		user=UserResponse.model_validate(user_response_data(user)),
	)


@router.post("/logout")
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
	token = await db.scalar(
		select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(payload.refresh_token))
	)
	if token is not None and token.revoked_at is None:
		token.revoked_at = utc_now()
		await db.commit()
	elif token is not None:
		await db.rollback()
	return {"message": "Logged out"}


@router.post("/logout-all")
async def logout_all(
	user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
	tokens = await db.scalars(
		select(RefreshToken).where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
	)
	now = utc_now()
	for token in tokens:
		token.revoked_at = now
	await db.commit()
	return {"message": "All sessions logged out"}


@router.get("/me", response_model=UserResponse)
async def current_user(user: User = Depends(get_current_user)) -> UserResponse:
	return UserResponse.model_validate(user_response_data(user))
