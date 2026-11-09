from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.actions.models import Goal, Task
from app.modules.documents.document_models import Document, DocumentPage
from app.modules.intelligence.context_models import UserContext
from app.modules.intelligence.models import DocumentInsight, IntelligenceInsight
from app.modules.search.schemas import GlobalSearchResponse, SearchEntity, SearchGroup, SearchParameters, SearchResult


class SearchService:
	def __init__(self, session: AsyncSession) -> None:
		self.session = session

	async def search(self, user_id: UUID, parameters: SearchParameters) -> GlobalSearchResponse:
		groups: dict[str, SearchGroup] = {}
		for entity in parameters.entities:
			if entity == SearchEntity.documents:
				group = await self._documents(user_id, parameters)
			elif entity == SearchEntity.tasks:
				group = await self._tasks(user_id, parameters)
			elif entity == SearchEntity.goals:
				group = await self._goals(user_id, parameters)
			elif entity == SearchEntity.insights:
				group = await self._insights(user_id, parameters)
			else:
				group = await self._memories(user_id, parameters)
			groups[entity.value] = group
		return GlobalSearchResponse(
			query=parameters.q,
			limit=parameters.limit,
			offset=parameters.offset,
			total=sum(group.total for group in groups.values()),
			groups=groups,
		)

	@staticmethod
	def _text_filter(query, columns: Sequence[object], text: str | None):
		if not text:
			return query
		pattern = f"%{text}%"
		return query.where(or_(*(column.ilike(pattern) for column in columns)))

	@staticmethod
	def _date_filters(filters: list[object], column, parameters: SearchParameters) -> None:
		if parameters.date_from:
			filters.append(column >= parameters.date_from)
		if parameters.date_to:
			filters.append(column <= parameters.date_to)

	@staticmethod
	def _order(column, parameters: SearchParameters):
		return column.asc() if parameters.order == "asc" else column.desc()

	async def _documents(self, user_id: UUID, parameters: SearchParameters) -> SearchGroup:
		filters: list[object] = [Document.user_id == user_id, Document.deleted_at.is_(None), Document.archived_at.is_(None)]
		self._date_filters(filters, Document.created_at, parameters)
		query = select(Document).where(*filters)
		if parameters.category:
			query = query.where(Document.document_type == parameters.category)
		if parameters.status:
			query = query.where(Document.processing_status == parameters.status)
		if parameters.q:
			pattern = f"%{parameters.q}%"
			query = query.outerjoin(DocumentPage, DocumentPage.document_id == Document.id).where(
				or_(Document.original_filename.ilike(pattern), Document.document_type.ilike(pattern), DocumentPage.extracted_text.ilike(pattern))
			).distinct()
		count_query = select(func.count()).select_from(query.order_by(None).subquery())
		total = int(await self.session.scalar(count_query) or 0)
		order_column = Document.original_filename if parameters.sort == "title" else Document.created_at
		rows = (await self.session.scalars(query.order_by(self._order(order_column, parameters), Document.id).limit(parameters.limit).offset(parameters.offset))).all()
		return SearchGroup(items=[self._result(row.id, row.original_filename, "documents", row.original_filename, f"/documents/{row.id}", row.document_type, row.processing_status, row.created_at, row.updated_at) for row in rows], total=total)

	async def _tasks(self, user_id: UUID, parameters: SearchParameters) -> SearchGroup:
		filters: list[object] = [Task.user_id == user_id]
		self._date_filters(filters, Task.created_at, parameters)
		if parameters.status:
			filters.append(Task.status == parameters.status)
		query = self._text_filter(select(Task).where(*filters), [Task.title, Task.description], parameters.q)
		total = int(await self.session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0)
		order_column = Task.title if parameters.sort == "title" else (Task.updated_at if parameters.sort == "updated_at" else Task.created_at)
		rows = (await self.session.scalars(query.order_by(self._order(order_column, parameters), Task.id).limit(parameters.limit).offset(parameters.offset))).all()
		return SearchGroup(items=[self._result(row.id, row.title, "tasks", row.description or row.title, f"/tasks/{row.id}", None, row.status, row.created_at, row.updated_at) for row in rows], total=total)

	async def _goals(self, user_id: UUID, parameters: SearchParameters) -> SearchGroup:
		filters: list[object] = [Goal.user_id == user_id]
		self._date_filters(filters, Goal.created_at, parameters)
		if parameters.status:
			filters.append(Goal.status == parameters.status)
		query = self._text_filter(select(Goal).where(*filters), [Goal.title, Goal.description], parameters.q)
		total = int(await self.session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0)
		order_column = Goal.title if parameters.sort == "title" else (Goal.updated_at if parameters.sort == "updated_at" else Goal.created_at)
		rows = (await self.session.scalars(query.order_by(self._order(order_column, parameters), Goal.id).limit(parameters.limit).offset(parameters.offset))).all()
		return SearchGroup(items=[self._result(row.id, row.title, "goals", row.description or row.title, f"/goals/{row.id}", None, row.status, row.created_at, row.updated_at) for row in rows], total=total)

	async def _insights(self, user_id: UUID, parameters: SearchParameters) -> SearchGroup:
		filters: list[object] = [IntelligenceInsight.user_id == user_id]
		self._date_filters(filters, IntelligenceInsight.created_at, parameters)
		if parameters.category:
			filters.append(IntelligenceInsight.category == parameters.category)
		if parameters.status:
			filters.append(IntelligenceInsight.status == parameters.status)
		query = self._text_filter(select(IntelligenceInsight).where(*filters), [IntelligenceInsight.title, IntelligenceInsight.description], parameters.q)
		total = int(await self.session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0)
		order_column = IntelligenceInsight.title if parameters.sort == "title" else IntelligenceInsight.created_at
		rows = (await self.session.scalars(query.order_by(self._order(order_column, parameters), IntelligenceInsight.id).limit(parameters.limit).offset(parameters.offset))).all()
		results = [self._result(row.id, row.title, "insights", row.description, f"/insights/{row.id}", row.category, row.status, row.created_at, None) for row in rows]
		return SearchGroup(items=results, total=total)

	async def _memories(self, user_id: UUID, parameters: SearchParameters) -> SearchGroup:
		filters: list[object] = [UserContext.user_id == user_id, UserContext.deleted_at.is_(None), UserContext.is_active.is_(True)]
		self._date_filters(filters, UserContext.created_at, parameters)
		if parameters.category:
			filters.append(UserContext.category == parameters.category)
		if parameters.status:
			filters.append(UserContext.confirmation_status == parameters.status)
		query = select(UserContext).where(*filters)
		if parameters.q:
			pattern = f"%{parameters.q}%"
			query = query.where(or_(UserContext.title.ilike(pattern), cast(UserContext.content, String).ilike(pattern), UserContext.category.ilike(pattern)))
		total = int(await self.session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0)
		order_column = UserContext.title if parameters.sort == "title" else (UserContext.updated_at if parameters.sort == "updated_at" else UserContext.created_at)
		rows = (await self.session.scalars(query.order_by(self._order(order_column, parameters), UserContext.id).limit(parameters.limit).offset(parameters.offset))).all()
		return SearchGroup(items=[self._result(row.id, row.title, "memories", str(row.content), f"/memory?memoryId={row.id}", row.category, row.confirmation_status, row.created_at, row.updated_at) for row in rows], total=total)

	@staticmethod
	def _result(id: UUID, title: str, entity_type: str, summary: str, navigation_ref: str, category: str | None, status: str | None, created_at, updated_at) -> SearchResult:
		return SearchResult(id=id, title=title, entity_type=entity_type, summary=summary[:500], navigation_ref=navigation_ref, category=category, status=status, created_at=created_at, updated_at=updated_at)
