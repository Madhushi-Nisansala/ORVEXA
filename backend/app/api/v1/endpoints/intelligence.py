from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.config import get_settings
from app.database.models import User
from app.database.session import get_db
from app.modules.documents.document_models import Document
from app.modules.documents.document_service import DocumentNotFoundError, DocumentService
from app.modules.extraction.models import DocumentExtraction
from app.modules.intelligence.analysis_service import AnalysisNotAvailableError, analyze_document
from app.modules.intelligence.models import DocumentAnalysis, DocumentInsight
from app.modules.intelligence.provider import provider_from_settings
from app.modules.intelligence.stage3_schemas import (
	AnalysisItemsResponse,
	AnalysisRequestResponse,
	AnalysisResponse,
	AnalysisResult,
	EvidenceCollectionResponse,
	EvidenceReference,
	InsightListResponse,
	InsightResponse,
)

router = APIRouter(tags=["intelligence"])


def as_response(analysis: DocumentAnalysis) -> AnalysisResponse:
	return AnalysisResponse(
		id=analysis.id,
		document_id=analysis.document_id,
		extraction_id=analysis.extraction_id,
		version=analysis.version,
		status=analysis.status,
		provider_identifier=analysis.provider_identifier,
		model_name=analysis.model_name,
		error_code=analysis.error_code,
		error_summary=analysis.error_summary,
		result=AnalysisResult.model_validate(analysis.result) if analysis.result else None,
		created_at=analysis.created_at,
		completed_at=analysis.completed_at,
	)


async def owned_document(document_id: UUID, user: User, db: AsyncSession) -> Document:
	try:
		return await DocumentService(db, get_settings()).get_owned(document_id, user.id)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc


async def owned_analysis(analysis_id: UUID, user: User, db: AsyncSession) -> DocumentAnalysis:
	analysis = await db.scalar(
		select(DocumentAnalysis).where(DocumentAnalysis.id == analysis_id, DocumentAnalysis.user_id == user.id)
	)
	if analysis is None:
		raise HTTPException(status_code=404, detail="Analysis not found")
	return analysis


@router.post("/documents/{document_id}/analyze", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze(
	document_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
	document = await owned_document(document_id, user, db)
	try:
		analysis = await analyze_document(db, document, get_settings())
	except AnalysisNotAvailableError as exc:
		raise HTTPException(status_code=409, detail=str(exc)) from exc
	return as_response(analysis)


@router.get("/documents/{document_id}/analysis", response_model=AnalysisResponse)
async def document_analysis(
	document_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
	await owned_document(document_id, user, db)
	analysis = await db.scalar(
		select(DocumentAnalysis)
		.where(DocumentAnalysis.document_id == document_id, DocumentAnalysis.user_id == user.id)
		.order_by(DocumentAnalysis.version.desc())
	)
	if analysis is None:
		raise HTTPException(status_code=404, detail="Analysis not found")
	return as_response(analysis)


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
	analysis_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
	return as_response(await owned_analysis(analysis_id, user, db))


@router.post("/analyses/{analysis_id}/retry", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def retry_analysis(
	analysis_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
	previous = await owned_analysis(analysis_id, user, db)
	document = await owned_document(previous.document_id, user, db)
	try:
		analysis = await analyze_document(db, document, get_settings(), force=True)
	except AnalysisNotAvailableError as exc:
		raise HTTPException(status_code=409, detail=str(exc)) from exc
	return as_response(analysis)


def category_items(analysis: DocumentAnalysis, category: str, offset: int, limit: int) -> AnalysisItemsResponse:
	result = AnalysisResult.model_validate(analysis.result or {})
	values = [item.model_dump(mode="json") for item in getattr(result, category)]
	return AnalysisItemsResponse(items=values[offset : offset + limit], total=len(values))


@router.get("/analyses/{analysis_id}/facts", response_model=AnalysisItemsResponse)
async def facts(analysis_id: UUID, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> AnalysisItemsResponse:
	return category_items(await owned_analysis(analysis_id, user, db), "facts", offset, limit)


@router.get("/analyses/{analysis_id}/dates", response_model=AnalysisItemsResponse)
async def dates(analysis_id: UUID, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> AnalysisItemsResponse:
	return category_items(await owned_analysis(analysis_id, user, db), "dates", offset, limit)


@router.get("/analyses/{analysis_id}/obligations", response_model=AnalysisItemsResponse)
async def obligations(analysis_id: UUID, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> AnalysisItemsResponse:
	return category_items(await owned_analysis(analysis_id, user, db), "obligations", offset, limit)


@router.get("/analyses/{analysis_id}/requirements", response_model=AnalysisItemsResponse)
async def requirements(analysis_id: UUID, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> AnalysisItemsResponse:
	return category_items(await owned_analysis(analysis_id, user, db), "requirements", offset, limit)


@router.get("/analyses/{analysis_id}/risks", response_model=AnalysisItemsResponse)
async def risks(analysis_id: UUID, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> AnalysisItemsResponse:
	return category_items(await owned_analysis(analysis_id, user, db), "risks", offset, limit)


@router.get("/analyses/{analysis_id}/evidence", response_model=EvidenceCollectionResponse)
async def evidence(analysis_id: UUID, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> EvidenceCollectionResponse:
	analysis = await owned_analysis(analysis_id, user, db)
	result = AnalysisResult.model_validate(analysis.result or {})
	references: list[EvidenceReference] = list(result.classification.evidence)
	for category in ("facts", "entities", "dates", "requirements", "obligations", "financial_information", "risks"):
		for item in getattr(result, category):
			references.extend(item.evidence)
	return EvidenceCollectionResponse(items=references[offset : offset + limit], total=len(references))


@router.get("/documents/{document_id}/insights", response_model=InsightListResponse)
async def document_insights(
	document_id: UUID,
	offset: int = Query(0, ge=0),
	limit: int = Query(50, ge=1, le=100),
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> InsightListResponse:
	await owned_document(document_id, user, db)
	query = select(DocumentInsight).where(
		DocumentInsight.document_id == document_id,
		DocumentInsight.user_id == user.id,
		DocumentInsight.status == "active",
	).order_by(DocumentInsight.created_at.desc())
	items = list(await db.scalars(query.offset(offset).limit(limit)))
	total = await db.scalar(select(func.count()).select_from(query.subquery()))
	return InsightListResponse(items=[InsightResponse.model_validate(item) for item in items], total=total or 0)


@router.get("/insights/{insight_id}", response_model=InsightResponse)
async def get_insight(insight_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> InsightResponse:
	insight = await db.scalar(select(DocumentInsight).where(DocumentInsight.id == insight_id, DocumentInsight.user_id == user.id))
	if insight is None:
		raise HTTPException(status_code=404, detail="Insight not found")
	return InsightResponse.model_validate(insight)


@router.delete("/insights/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_insight(insight_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> None:
	insight = await db.scalar(select(DocumentInsight).where(DocumentInsight.id == insight_id, DocumentInsight.user_id == user.id))
	if insight is None:
		raise HTTPException(status_code=404, detail="Insight not found")
	insight.status = "deleted"
	await db.commit()
