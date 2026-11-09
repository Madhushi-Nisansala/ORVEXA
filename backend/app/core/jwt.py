from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings

ACCESS_TOKEN_TYPE = "access"


def create_access_token(subject: str, roles: list[str]) -> str:
	settings = get_settings()
	now = datetime.now(timezone.utc)
	payload = {
		"sub": subject,
		"iat": now,
		"exp": now + timedelta(minutes=settings.access_token_expire_minutes),
		"jti": str(uuid4()),
		"type": ACCESS_TOKEN_TYPE,
		"roles": roles,
	}
	return jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
	settings = get_settings()
	try:
		payload = jwt.decode(
			token,
			settings.jwt_secret_key.get_secret_value(),
			algorithms=[settings.jwt_algorithm],
			options={"require": ["sub", "iat", "exp", "jti", "type"]},
		)
	except jwt.PyJWTError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid authentication credentials",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc
	if payload.get("type") != ACCESS_TOKEN_TYPE:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid authentication credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return payload
