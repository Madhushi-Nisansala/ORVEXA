from datetime import datetime, timezone

from sqlalchemy import DateTime

UTCDateTime = DateTime(timezone=True)


def utc_now() -> datetime:
	return datetime.now(timezone.utc)


def require_utc(value: datetime) -> datetime:
	if value.tzinfo is None or value.utcoffset() is None:
		raise ValueError("Timestamp must be timezone-aware")
	return value.astimezone(timezone.utc)
