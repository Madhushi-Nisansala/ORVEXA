from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.jwt import decode_access_token
from app.database.models import User
from app.database.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
	db: AsyncSession = Depends(get_db),
) -> User:
	unauthorized = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Invalid authentication credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	if credentials is None or credentials.scheme.lower() != "bearer":
		raise unauthorized
	payload = decode_access_token(credentials.credentials)
	try:
		user_id = UUID(payload["sub"])
	except (KeyError, ValueError) as exc:
		raise unauthorized from exc
	user = await db.scalar(
		select(User).options(selectinload(User.roles)).where(User.id == user_id)
	)
	if user is None or not user.is_active:
		raise unauthorized
	return user


def require_roles(*required_roles: str) -> Callable:
	async def dependency(user: User = Depends(get_current_user)) -> User:
		actual_roles = {role.name for role in user.roles}
		if not actual_roles.intersection(required_roles):
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
		return user

	return dependency
