from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.database.base import Base
from app.modules.documents.document_models import Document, DocumentPage
from app.modules.extraction.models import DocumentExtraction
from app.modules.intelligence.analysis_service import analyze_document, segment_pages, validate_evidence
from app.modules.intelligence.models import DocumentAnalysis
from app.modules.intelligence.provider import AnalysisPage, ProviderUnavailableError
from app.modules.intelligence.stage3_schemas import (
	AnalysisResult,
	ConfidenceLevel,
	DocumentClassification,
	EvidenceReference,
	InformationClassification,
	Fact,
)


class ControlledProvider:
	identifier = "test-provider"
	model_name = "controlled-model"

	async def analyze(self, document_id, pages: Sequence[AnalysisPage], settings: Settings) -> AnalysisResult:
		page = pages[0]
		evidence = EvidenceReference(
			document_id=document_id,
			extraction_id=page.extraction_id,
			page_number=page.page_number,
			source_text="Rent is 100 USD",
		)
		return AnalysisResult(
			classification=DocumentClassification(
				primary_type="rental_agreement", confidence=0.9, explanation="The page contains a rent term.", evidence=[evidence]
			),
			facts=[Fact(
				fact_type="amount", value="100 USD", original_value="100 USD", classification=InformationClassification.source_fact,
				confidence=0.9, confidence_level=ConfidenceLevel.high, evidence=[evidence],
			)],
			coverage_start_page=1,
			coverage_end_page=1,
			coverage_complete=True,
		)


class InvalidEvidenceProvider(ControlledProvider):
	async def analyze(self, document_id, pages, settings):
		result = await super().analyze(document_id, pages, settings)
		result.facts[0].evidence[0].source_text = "not present"
		return result


class MalformedProvider(ControlledProvider):
	async def analyze(self, document_id, pages, settings):
		return {"unexpected": "provider output"}


@pytest.mark.asyncio
async def test_evidence_validation_requires_exact_page_content() -> None:
	document_id = uuid4()
	extraction_id = uuid4()
	page = DocumentPage(
		id=uuid4(), document_id=document_id, page_number=1, extracted_text="Rent is 100 USD", extraction_method="text",
		created_at=datetime.now(timezone.utc),
	)
	evidence = EvidenceReference(
		document_id=document_id, extraction_id=extraction_id, page_number=1, source_text="Rent is 100 USD"
	)
	result = AnalysisResult(
		classification=DocumentClassification(primary_type="other", explanation="", evidence=[evidence]),
	)
	validated = validate_evidence(result, document_id, extraction_id, [page])
	assert validated.classification.evidence[0].validation_status == "validated"
	with pytest.raises(ValueError):
		validate_evidence(result.model_copy(update={"classification": DocumentClassification(primary_type="other", explanation="", evidence=[evidence.model_copy(update={"source_text": "missing"})])}), document_id, extraction_id, [page])


@pytest.mark.asyncio
async def test_analysis_is_versioned_and_does_not_overwrite_history(tmp_path: Path) -> None:
	engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
	factory = async_sessionmaker(engine, expire_on_commit=False)
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)
	document_id = uuid4()
	user_id = uuid4()
	extraction_id = uuid4()
	now = datetime.now(timezone.utc)
	async with factory() as session:
		document = Document(
			id=document_id, user_id=user_id, original_filename="lease.txt", storage_key="x", mime_type="text/plain",
			file_size=16, sha256_hash="a" * 64, document_type="txt", created_at=now, updated_at=now,
		)
		extraction = DocumentExtraction(
			id=extraction_id, user_id=user_id, document_id=document_id, extractor_type="text", extractor_version="test",
			processing_version="stage2-v1", status="completed", created_at=now,
		)
		page = DocumentPage(
			id=uuid4(), document_id=document_id, page_number=1, extracted_text="Rent is 100 USD", extraction_method="text",
			created_at=now,
		)
		session.add_all([document, extraction, page])
		await session.commit()
		settings = Settings(DOCUMENT_STORAGE_ROOT=str(tmp_path), ANALYSIS_PROVIDER="unavailable")
		first = await analyze_document(session, document, settings, ControlledProvider())
		assert first.status == "completed"
		same = await analyze_document(session, document, settings, ControlledProvider())
		assert same.id == first.id
		second = await analyze_document(session, document, settings, ControlledProvider(), force=True)
		assert second.version == 2
		assert (await session.scalar(__import__("sqlalchemy").select(DocumentAnalysis).where(DocumentAnalysis.document_id == document_id).order_by(DocumentAnalysis.version))).id == first.id
	await engine.dispose()


@pytest.mark.asyncio
async def test_malformed_provider_output_is_not_persisted_as_success(tmp_path: Path) -> None:
	engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
	factory = async_sessionmaker(engine, expire_on_commit=False)
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)
	now = datetime.now(timezone.utc)
	document_id, user_id, extraction_id = uuid4(), uuid4(), uuid4()
	async with factory() as session:
		document = Document(
			id=document_id, user_id=user_id, original_filename="notice.txt", storage_key="x", mime_type="text/plain",
			file_size=5, sha256_hash="c" * 64, document_type="txt", created_at=now, updated_at=now,
		)
		session.add_all([
			document,
			DocumentExtraction(id=extraction_id, user_id=user_id, document_id=document_id, extractor_type="text", extractor_version="test", processing_version="stage2-v1", status="completed", created_at=now),
			DocumentPage(id=uuid4(), document_id=document_id, page_number=1, extracted_text="Notice", extraction_method="text", created_at=now),
		])
		await session.commit()
		analysis = await analyze_document(session, document, Settings(DOCUMENT_STORAGE_ROOT=str(tmp_path)), MalformedProvider())
		assert analysis.status == "failed"
		assert analysis.result is None
		assert analysis.error_code == "invalid_analysis_output"
	await engine.dispose()


@pytest.mark.asyncio
async def test_provider_unavailable_is_persisted_without_fabricated_result(tmp_path: Path) -> None:
	engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
	factory = async_sessionmaker(engine, expire_on_commit=False)
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)
	now = datetime.now(timezone.utc)
	document_id, user_id, extraction_id = uuid4(), uuid4(), uuid4()
	async with factory() as session:
		document = Document(
			id=document_id, user_id=user_id, original_filename="notice.txt", storage_key="x", mime_type="text/plain",
			file_size=5, sha256_hash="b" * 64, document_type="txt", created_at=now, updated_at=now,
		)
		session.add_all([
			document,
			DocumentExtraction(id=extraction_id, user_id=user_id, document_id=document_id, extractor_type="text", extractor_version="test", processing_version="stage2-v1", status="completed", created_at=now),
			DocumentPage(id=uuid4(), document_id=document_id, page_number=1, extracted_text="Notice", extraction_method="text", created_at=now),
		])
		await session.commit()
		analysis = await analyze_document(session, document, Settings(DOCUMENT_STORAGE_ROOT=str(tmp_path)), None)
		assert analysis.status == "provider_unavailable"
		assert analysis.result is None
		assert analysis.error_code == "provider_unavailable"
	await engine.dispose()
