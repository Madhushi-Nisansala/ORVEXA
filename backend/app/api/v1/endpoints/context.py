from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.modules.intelligence.context_models import ContextPreference, InsightEvidence, UserContext
from app.modules.intelligence.context_schemas import (
	ContextCreate,
	ContextPreferenceResponse,
	ContextPreferenceUpdate,
	ContextResponse,
	ContextUpdate,
	InsightFeedbackCreate,
	InsightGenerationResponse,
	InsightResponse,
)
from app.modules.intelligence.context_service import get_preferences, retrieve_context, search_memories
from app.modules.intelligence.models import AnalysisRun, IntelligenceInsight, IntelligenceRequest, UserFeedback

router = APIRouter(tags=["context", "insights"])


def now() -> datetime:
	return datetime.now(timezone.utc)


def context_response(value: UserContext) -> ContextResponse:
	return ContextResponse.model_validate(value)


async def owned_context(context_id: UUID, user_id: UUID, db: AsyncSession) -> UserContext:
	value = await db.scalar(
		select(UserContext).where(
			UserContext.id == context_id,
			UserContext.user_id == user_id,
			UserContext.deleted_at.is_(None),
		)
	)
	if value is None:
		raise HTTPException(status_code=404, detail="Context not found")
	return value


@router.get("/context", response_model=list[ContextResponse])
@router.get("/memory", response_model=list[ContextResponse], include_in_schema=True)
async def list_context(
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
	active_only: bool = Query(True),
	search: str | None = Query(None, max_length=200),
	category: str | None = Query(None, max_length=64),
) -> list[ContextResponse]:
	if search or category:
		return [context_response(row) for row in await search_memories(db, user.id, search, category=category)]
	query = select(UserContext).where(UserContext.user_id == user.id, UserContext.deleted_at.is_(None))
	if active_only:
		query = query.where(UserContext.is_active.is_(True))
	rows = (await db.scalars(query.order_by(UserContext.updated_at.desc()))).all()
	return [context_response(row) for row in rows]


@router.post("/context", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
@router.post("/memory", response_model=ContextResponse, status_code=status.HTTP_201_CREATED, include_in_schema=True)
async def create_context(
	payload: ContextCreate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> ContextResponse:
	if payload.evidence_reference and payload.context_type not in {
		"DOCUMENT_DERIVED_CONTEXT",
		"USER_CONFIRMED_CONTEXT",
	}:
		raise HTTPException(status_code=422, detail="Evidence-linked context must be document-derived or confirmed")
	values = payload.model_dump(exclude={"title"})
	values["title"] = payload.title or payload.category.replace("_", " ").title()
	value = UserContext(
		user_id=user.id,
		**values,
		confirmation_status="confirmed" if payload.context_type == "USER_PROVIDED_CONTEXT" else "unconfirmed",
	)
	db.add(value)
	await db.commit()
	await db.refresh(value)
	return context_response(value)


@router.get("/context/{context_id}", response_model=ContextResponse)
@router.get("/memory/{context_id}", response_model=ContextResponse, include_in_schema=True)
async def get_context(
	context_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> ContextResponse:
	return context_response(await owned_context(context_id, user.id, db))


@router.patch("/context/{context_id}", response_model=ContextResponse)
@router.patch("/memory/{context_id}", response_model=ContextResponse, include_in_schema=True)
async def update_context(
	context_id: UUID,
	payload: ContextUpdate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> ContextResponse:
	value = await owned_context(context_id, user.id, db)
	for key, changed in payload.model_dump(exclude_unset=True).items():
		setattr(value, key, changed)
	if value.confirmation_status == "confirmed" and value.context_type == "UNCONFIRMED_CONTEXT":
		value.context_type = "USER_CONFIRMED_CONTEXT"
	await db.commit()
	await db.refresh(value)
	return context_response(value)


@router.delete("/context/{context_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/memory/{context_id}", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=True)
async def delete_context(
	context_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> None:
	value = await owned_context(context_id, user.id, db)
	value.is_active = False
	value.deleted_at = now()
	await db.commit()


@router.post("/context/{context_id}/archive", response_model=ContextResponse)
@router.post("/memory/{context_id}/archive", response_model=ContextResponse, include_in_schema=True)
async def archive_context(
	context_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> ContextResponse:
	value = await owned_context(context_id, user.id, db)
	value.is_active = False
	await db.commit()
	await db.refresh(value)
	return context_response(value)


@router.delete("/context/{context_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/memory/{context_id}/permanent", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=True)
async def permanently_delete_context(
	context_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> None:
	value = await db.scalar(select(UserContext).where(UserContext.id == context_id, UserContext.user_id == user.id))
	if value is None:
		raise HTTPException(status_code=404, detail="Memory not found")
	await db.delete(value)
	await db.commit()


@router.post("/context/{context_id}/confirm", response_model=ContextResponse)
async def confirm_context(
	context_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> ContextResponse:
	value = await owned_context(context_id, user.id, db)
	value.confirmation_status = "confirmed"
	value.context_type = "USER_CONFIRMED_CONTEXT"
	await db.commit()
	await db.refresh(value)
	return context_response(value)


@router.post("/context/{context_id}/reject", response_model=ContextResponse)
async def reject_context(
	context_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> ContextResponse:
	value = await owned_context(context_id, user.id, db)
	value.confirmation_status = "rejected"
	value.is_active = False
	await db.commit()
	await db.refresh(value)
	return context_response(value)


@router.get("/context/preferences", response_model=ContextPreferenceResponse)
async def context_preferences(
	user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ContextPreferenceResponse:
	return ContextPreferenceResponse.model_validate(await get_preferences(db, user.id))


@router.patch("/context/preferences", response_model=ContextPreferenceResponse)
async def update_context_preferences(
	payload: ContextPreferenceUpdate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> ContextPreferenceResponse:
	preference = await get_preferences(db, user.id)
	for key, value in payload.model_dump(exclude_unset=True).items():
		setattr(preference, key, value)
	await db.commit()
	await db.refresh(preference)
	return ContextPreferenceResponse.model_validate(preference)


@router.get("/context/relevant", response_model=list[ContextResponse])
async def relevant_context(
	task: str | None = None,
	limit: int = Query(20, ge=1, le=50),
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> list[ContextResponse]:
	return [context_response(row) for row in await retrieve_context(db, user.id, task, limit)]


async def insight_response(insight: IntelligenceInsight, db: AsyncSession) -> InsightResponse:
	evidence_ids = list(
		await db.scalars(select(InsightEvidence.evidence_source_id).where(InsightEvidence.insight_id == insight.id))
	)
	return InsightResponse(
		id=insight.id,
		title=insight.title,
		description=insight.description,
		category=insight.category,
		importance=insight.importance,
		confidence=insight.confidence,
		uncertainty=insight.uncertainty,
		status=insight.status,
		evidence_source_ids=evidence_ids,
		created_at=insight.created_at,
	)


@router.get("/insights", response_model=list[InsightResponse])
async def list_insights(
	user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[InsightResponse]:
	rows = (await db.scalars(select(IntelligenceInsight).where(IntelligenceInsight.user_id == user.id).order_by(IntelligenceInsight.created_at.desc()))).all()
	return [await insight_response(row, db) for row in rows]


@router.post("/insights/generate", response_model=InsightGenerationResponse)
async def generate_insight(
	task: str | None = None,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> InsightGenerationResponse:
	context = await retrieve_context(db, user.id, task, limit=10)
	evidence_ids = [row.evidence_reference for row in context if row.evidence_reference and row.confirmation_status == "confirmed"]
	if not evidence_ids:
		return InsightGenerationResponse(
			sufficient_information=False,
			limitation="No confirmed evidence-linked context is available for this request.",
		)
	request = IntelligenceRequest(user_id=user.id, request_type="personal_insight", input_text=task)
	db.add(request)
	await db.flush()
	run = AnalysisRun(user_id=user.id, request_id=request.id, status="completed", completed_at=now())
	db.add(run)
	await db.flush()
	insight = IntelligenceInsight(
		user_id=user.id,
		analysis_run_id=run.id,
		title="Evidence-backed personal context",
		description="Confirmed context relevant to the request is available for review; no unverified conclusion was added.",
		category="finding",
		confidence=1.0,
		uncertainty=0.0,
	)
	db.add(insight)
	await db.flush()
	for evidence_id in dict.fromkeys(evidence_ids):
		db.add(InsightEvidence(user_id=user.id, insight_id=insight.id, evidence_source_id=evidence_id))
	await db.commit()
	await db.refresh(insight)
	return InsightGenerationResponse(sufficient_information=True, insight=await insight_response(insight, db))


@router.post("/insights/{insight_id}/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
	insight_id: UUID,
	payload: InsightFeedbackCreate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
	insight = await db.scalar(select(IntelligenceInsight).where(IntelligenceInsight.id == insight_id, IntelligenceInsight.user_id == user.id))
	if insight is None:
		raise HTTPException(status_code=404, detail="Insight not found")
	db.add(UserFeedback(user_id=user.id, insight_id=insight.id, value=payload.value, correction=payload.correction))
	await db.commit()
	return {"status": "recorded"}
