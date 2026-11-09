import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_password_hasher = PasswordHasher()


def utc_now() -> datetime:
	return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
	if not password or len(password) > 1024:
		raise ValueError("Password input is invalid")
	return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
	if not password or not password_hash:
		return False
	try:
		return _password_hasher.verify(password_hash, password)
	except (VerifyMismatchError, VerificationError, InvalidHashError):
		return False


def create_refresh_token() -> str:
	return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
	return hashlib.sha256(token.encode("utf-8")).hexdigest()


def refresh_expiry(days: int) -> datetime:
	return utc_now() + timedelta(days=days)
