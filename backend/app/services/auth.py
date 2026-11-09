from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.jwt import create_access_token
from app.core.security import (
	create_refresh_token,
	hash_refresh_token,
	refresh_expiry,
	utc_now,
)
from app.database.models import RefreshToken, Role, User


async def user_with_roles(db: AsyncSession, user_id: UUID) -> User | None:
	return await db.scalar(select(User).options(selectinload(User.roles)).where(User.id == user_id))


def user_response_data(user: User) -> dict:
	return {
		"id": user.id,
		"email": user.email,
		"full_name": user.full_name,
		"preferred_language": user.preferred_language,
		"is_active": user.is_active,
		"is_verified": user.is_verified,
		"created_at": user.created_at,
		"updated_at": user.updated_at,
		"last_login_at": user.last_login_at,
		"roles": [role.name for role in user.roles],
	}


async def issue_token_pair(
	db: AsyncSession, user: User, device_name: str | None = None
) -> tuple[str, str]:
	settings = get_settings()
	raw_refresh = create_refresh_token()
	refresh_row = RefreshToken(
		user_id=user.id,
		token_hash=hash_refresh_token(raw_refresh),
		expires_at=refresh_expiry(settings.refresh_token_expire_days),
		created_at=utc_now(),
		device_name=device_name,
	)
	db.add(refresh_row)
	access = create_access_token(str(user.id), [role.name for role in user.roles])
	return access, raw_refresh


async def rotate_refresh_token(
	db: AsyncSession, raw_refresh: str
) -> tuple[User, str, str] | None:
	settings = get_settings()
	token = await db.scalar(
		select(RefreshToken)
		.options(selectinload(RefreshToken.user).selectinload(User.roles))
		.where(RefreshToken.token_hash == hash_refresh_token(raw_refresh))
		.with_for_update()
	)
	now = utc_now()
	if token is None:
		return None
	if token.revoked_at is not None:
		await db.execute(
			update(RefreshToken)
			.where(RefreshToken.user_id == token.user_id, RefreshToken.revoked_at.is_(None))
			.values(revoked_at=now)
		)
		return None
	if token.expires_at <= now or not token.user.is_active:
		token.revoked_at = now
		return None

	token.revoked_at = now
	token.last_used_at = now
	new_raw = create_refresh_token()
	replacement = RefreshToken(
		user_id=token.user_id,
		token_hash=hash_refresh_token(new_raw),
		expires_at=refresh_expiry(settings.refresh_token_expire_days),
		created_at=now,
		device_name=token.device_name,
	)
	db.add(replacement)
	await db.flush()
	token.replaced_by_token_id = replacement.id
	access = create_access_token(str(token.user_id), [role.name for role in token.user.roles])
	return token.user, access, new_raw


async def assign_default_role(db: AsyncSession, user: User) -> None:
	role = await db.scalar(select(Role).where(Role.name == "user"))
	if role is None:
		role = Role(name="user")
		db.add(role)
		await db.flush()
	user.roles.append(role)
