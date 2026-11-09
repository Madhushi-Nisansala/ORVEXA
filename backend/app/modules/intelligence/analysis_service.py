from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.modules.documents.document_models import Document, DocumentPage
from app.modules.extraction.models import DocumentExtraction
from app.modules.intelligence.models import DocumentAnalysis
from app.modules.intelligence.insight_service import create_insights_for_analysis
from app.modules.intelligence.provider import (
	AnalysisPage,
	DocumentIntelligenceProvider,
	ProviderOutputError,
	ProviderUnavailableError,
	provider_from_settings,
)
from app.modules.intelligence.stage3_schemas import AnalysisResult, AnalysisStatus, EvidenceReference, EvidenceValidationStatus


class AnalysisNotAvailableError(LookupError):
	pass


class EvidenceValidationError(ValueError):
	pass


def segment_pages(pages: Sequence[AnalysisPage], max_characters: int) -> list[AnalysisPage]:
	if max_characters < 1:
		raise ValueError("Analysis input limit must be positive")
	segments: list[AnalysisPage] = []
	for page in pages:
		text = page.text
		if not text:
			continue
		for offset in range(0, len(text), max_characters):
			segments.append(
				AnalysisPage(
					page_number=page.page_number,
					text=text[offset : offset + max_characters],
					extraction_id=page.extraction_id,
					extraction_method=page.extraction_method,
				)
			)
	return segments


def _validate_reference(
	reference: EvidenceReference,
	document_id: UUID,
	extraction_id: UUID,
	pages_by_number: dict[int, DocumentPage],
) -> EvidenceReference:
	if reference.document_id != document_id or reference.extraction_id != extraction_id:
		raise EvidenceValidationError("Evidence references a different document or extraction")
	page = pages_by_number.get(reference.page_number)
	if page is None:
		raise EvidenceValidationError("Evidence references a page that does not exist")
	if reference.start_offset is not None or reference.end_offset is not None:
		start = reference.start_offset or 0
		end = reference.end_offset if reference.end_offset is not None else start + len(reference.source_text)
		if end > len(page.extracted_text) or page.extracted_text[start:end] != reference.source_text:
			raise EvidenceValidationError("Evidence offsets do not match extracted page text")
	elif reference.source_text not in page.extracted_text:
		raise EvidenceValidationError("Evidence text is not present on the referenced page")
	return reference.model_copy(update={"validation_status": EvidenceValidationStatus.validated})


def validate_evidence(
	result: AnalysisResult,
	document_id: UUID,
	extraction_id: UUID,
	pages: Sequence[DocumentPage],
) -> AnalysisResult:
	pages_by_number = {page.page_number: page for page in pages}

	def references(items: Sequence[EvidenceReference]) -> list[EvidenceReference]:
		return [_validate_reference(item, document_id, extraction_id, pages_by_number) for item in items]

	data = result.model_dump()
	data["classification"]["evidence"] = references(result.classification.evidence)
	for key in ("facts", "entities", "dates", "requirements", "obligations", "financial_information", "risks"):
		data[key] = [item.model_copy(update={"evidence": references(item.evidence)}).model_dump() for item in getattr(result, key)]
	return AnalysisResult.model_validate(data)


async def latest_extraction(session: AsyncSession, document_id: UUID) -> DocumentExtraction | None:
	return await session.scalar(
		select(DocumentExtraction)
		.where(DocumentExtraction.document_id == document_id, DocumentExtraction.status.in_(("completed", "partial")))
		.order_by(DocumentExtraction.created_at.desc())
	)


async def analyze_document(
	session: AsyncSession,
	document: Document,
	settings: Settings,
	provider: DocumentIntelligenceProvider | None = None,
	force: bool = False,
) -> DocumentAnalysis:
	extraction = await latest_extraction(session, document.id)
	if extraction is None:
		raise AnalysisNotAvailableError("A completed document extraction is required before analysis")
	pages = list(
		await session.scalars(
			select(DocumentPage)
			.where(DocumentPage.document_id == document.id, DocumentPage.extraction_status == "completed")
			.order_by(DocumentPage.page_number)
		)
	)
	if not pages:
		raise AnalysisNotAvailableError("No completed extracted pages are available for analysis")
	if not any(page.extracted_text.strip() for page in pages):
		raise AnalysisNotAvailableError("No text was extracted from the document")
	latest = await session.scalar(
		select(DocumentAnalysis).where(DocumentAnalysis.document_id == document.id).order_by(DocumentAnalysis.version.desc())
	)
	if latest is not None and latest.status in {AnalysisStatus.processing.value, AnalysisStatus.completed.value} and not force:
		return latest
	version = (latest.version + 1) if latest is not None else 1
	analysis = DocumentAnalysis(
		id=uuid4(), user_id=document.user_id, document_id=document.id, extraction_id=extraction.id,
		version=version, status=AnalysisStatus.processing.value, created_at=datetime.now(timezone.utc),
	)
	session.add(analysis)
	await session.commit()
	await session.refresh(analysis)
	inputs = [
		AnalysisPage(page_number=page.page_number, text=page.extracted_text, extraction_id=extraction.id, extraction_method=page.extraction_method)
		for page in pages
	]
	segments = segment_pages(inputs, settings.analysis_max_input_characters)
	active_provider = provider
	try:
		active_provider = provider or provider_from_settings(settings)
		result = await asyncio.wait_for(active_provider.analyze(document.id, segments, settings), settings.analysis_timeout_seconds)
		if not isinstance(result, AnalysisResult):
			result = AnalysisResult.model_validate(result)
		result = validate_evidence(result, document.id, extraction.id, pages)
		analysis.provider_identifier = active_provider.identifier
		analysis.model_name = active_provider.model_name
		analysis.result = result.model_dump(mode="json")
		analysis.status = AnalysisStatus.completed.value if result.coverage_complete else AnalysisStatus.partial.value
		analysis.completed_at = datetime.now(timezone.utc)
		await session.commit()
		await create_insights_for_analysis(session, analysis)
	except ProviderUnavailableError as exc:
		analysis.status = AnalysisStatus.provider_unavailable.value
		analysis.error_code = "provider_unavailable"
		analysis.error_summary = str(exc)[:500]
		analysis.provider_identifier = active_provider.identifier if active_provider else settings.analysis_provider
		analysis.model_name = active_provider.model_name if active_provider else settings.openai_model or settings.analysis_model
		await session.commit()
	except (EvidenceValidationError, ProviderOutputError, ValueError) as exc:
		analysis.status = AnalysisStatus.failed.value
		analysis.error_code = "invalid_analysis_output"
		analysis.error_summary = str(exc)[:500]
		await session.commit()
	except asyncio.TimeoutError:
		analysis.status = AnalysisStatus.failed.value
		analysis.error_code = "provider_timeout"
		analysis.error_summary = "Document analysis provider timed out"
		await session.commit()
	return analysis
