from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.intelligence.models import DocumentAnalysis, DocumentInsight
from app.modules.intelligence.stage3_schemas import AnalysisResult


async def create_insights_for_analysis(
	session: AsyncSession, analysis: DocumentAnalysis
) -> list[DocumentInsight]:
	if analysis.status not in {"completed", "partial"} or not analysis.result:
		return []
	existing = await session.scalar(
		select(DocumentInsight.id).where(DocumentInsight.analysis_id == analysis.id).limit(1)
	)
	if existing is not None:
		return list(await session.scalars(select(DocumentInsight).where(DocumentInsight.analysis_id == analysis.id)))
	result = AnalysisResult.model_validate(analysis.result)
	items: list[DocumentInsight] = []
	now = datetime.now(timezone.utc)
	if result.executive_summary or result.classification.explanation:
		items.append(DocumentInsight(
			id=uuid4(), user_id=analysis.user_id, document_id=analysis.document_id, analysis_id=analysis.id,
			title="Executive summary", description=result.executive_summary or result.classification.explanation, category="summary",
			importance=90, confidence=result.classification.confidence, created_at=now,
		))
	for category, values in (("topic", result.topics), ("opportunity", result.opportunities), ("recommendation", result.recommendations)):
		for value in values:
			items.append(DocumentInsight(
				id=uuid4(), user_id=analysis.user_id, document_id=analysis.document_id, analysis_id=analysis.id,
				title=f"{category.title()}: {value[:160]}", description=value, category=category,
				importance=60, created_at=now,
			))
	for category, values in (("risk", result.risks), ("action", result.obligations + result.requirements)):
		for value in values:
			description = getattr(value, "description", None) or getattr(value, "explanation", None) or getattr(value, "value", None)
			if not description:
				continue
			title = f"{category.title()}: {description[:160]}"
			items.append(DocumentInsight(
				id=uuid4(), user_id=analysis.user_id, document_id=analysis.document_id, analysis_id=analysis.id,
				title=title, description=description, category=category,
				importance=80 if category == "risk" else 70, confidence=value.confidence, created_at=now,
			))
	session.add_all(items)
	await session.commit()
	return items