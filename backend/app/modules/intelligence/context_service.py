from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.intelligence.context_models import ContextPreference, UserContext


def utc_now() -> datetime:
	return datetime.now(timezone.utc)


async def get_preferences(session: AsyncSession, user_id: UUID) -> ContextPreference:
	preference = await session.get(ContextPreference, user_id)
	if preference is None:
		preference = ContextPreference(user_id=user_id)
		session.add(preference)
		await session.flush()
	return preference


async def retrieve_context(
	session: AsyncSession,
	user_id: UUID,
	task: str | None = None,
	limit: int = 20,
	category: str | None = None,
) -> list[UserContext]:
	preference = await get_preferences(session, user_id)
	now = utc_now()
	allowed_types = {"USER_PROVIDED_CONTEXT", "USER_CONFIRMED_CONTEXT"}
	if preference.allow_document_derived_context:
		allowed_types.add("DOCUMENT_DERIVED_CONTEXT")
	if preference.allow_interaction_derived_context:
		allowed_types.add("INTERACTION_DERIVED_CONTEXT")
	query = select(UserContext).where(
		UserContext.user_id == user_id,
		UserContext.is_active.is_(True),
		UserContext.deleted_at.is_(None),
		UserContext.context_type.in_(allowed_types),
		or_(UserContext.expires_at.is_(None), UserContext.expires_at > now),
		UserContext.confirmation_status != "rejected",
	)
	if not preference.persistent_memory_enabled:
		query = query.where(UserContext.context_type.in_({"USER_PROVIDED_CONTEXT", "USER_CONFIRMED_CONTEXT"}))
	if category:
		query = query.where(UserContext.category == category)
	rows = list((await session.scalars(query)).all())
	terms = {term.lower() for term in (task or "").split() if len(term) > 2}

	def score(row: UserContext) -> tuple[int, float]:
		haystack = f"{row.title} {row.category} {row.content}".lower()
		relevance = sum(term in haystack for term in terms)
		confirmation = 2 if row.confirmation_status == "confirmed" else 0
		age = row.created_at.timestamp() if row.created_at else 0
		return relevance + confirmation, age

	return sorted(rows, key=score, reverse=True)[:limit]


async def search_memories(
	session: AsyncSession,
	user_id: UUID,
	query_text: str | None = None,
	category: str | None = None,
	limit: int = 50,
) -> list[UserContext]:
	"""Return only active, non-expired memories owned by the requesting user."""
	return await retrieve_context(session, user_id, query_text, limit, category)
