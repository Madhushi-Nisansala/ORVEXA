from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, status

from app.core.config import get_settings

_attempts: dict[str, deque[float]] = defaultdict(deque)


def enforce_auth_rate_limit(key: str) -> None:
	settings = get_settings()
	now = monotonic()
	attempts = _attempts[key]
	while attempts and now - attempts[0] > settings.auth_rate_limit_window_seconds:
		attempts.popleft()
	if len(attempts) >= settings.auth_rate_limit_attempts:
		raise HTTPException(
			status_code=status.HTTP_429_TOO_MANY_REQUESTS,
			detail="Too many authentication attempts",
		)
	attempts.append(now)
