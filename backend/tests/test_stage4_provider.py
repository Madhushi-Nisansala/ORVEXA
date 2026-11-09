from collections.abc import Sequence
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.database.base import Base
from app.modules.documents.document_models import Document, DocumentPage
from app.modules.extraction.models import DocumentExtraction
from app.modules.intelligence.analysis_service import analyze_document, validate_evidence
from app.modules.intelligence.models import DocumentAnalysis
from app.modules.intelligence.provider import (
	AnalysisPage,
	OpenAIProvider,
	ProviderOutputError,
	ProviderUnavailableError,
	provider_from_settings,
)
from app.modules.intelligence.stage3_schemas import (
	AnalysisResult,
	DocumentClassification,
	EvidenceReference,
	Fact,
	InformationClassification,
)


class FakeOpenAIClient:
	def __init__(self, content: str | None = None, error: Exception | None = None) -> None:
		self.content = content
		self.error = error
		self.calls = 0
		self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

	async def create(self, **request: object) -> object:
		self.calls += 1
		if self.error is not None:
			raise self.error
		return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


def valid_result(document_id, extraction_id) -> AnalysisResult:
	evidence = EvidenceReference(
		document_id=document_id,
		extraction_id=extraction_id,
		page_number=1,
		source_text="Rent is 100 USD",
	)
	return AnalysisResult(
		classification=DocumentClassification(primary_type="contract", explanation="The source is a contract."),
		facts=[Fact(
			fact_type="amount",
			value="100 USD",
			original_value="100 USD",
			classification=InformationClassification.source_fact,
			evidence=[evidence],
		)],
		coverage_start_page=1,
		coverage_end_page=1,
		coverage_complete=True,
	)


def settings(**overrides: object) -> Settings:
	values = {
		"ANALYSIS_PROVIDER": "openai",
		"OPENAI_API_KEY": "test-key-not-a-real-credential",
		"OPENAI_MODEL": "test-model",
		"ANALYSIS_RETRY_ATTEMPTS": 0,
	}
	values.update(overrides)
	return Settings(**values)


@pytest.mark.asyncio
async def test_openai_provider_parses_valid_structured_output() -> None:
	document_id, extraction_id = uuid4(), uuid4()
	client = FakeOpenAIClient(content=valid_result(document_id, extraction_id).model_dump_json())
	provider = OpenAIProvider(settings(), client=client)
	result = await provider.analyze(
		document_id,
		[AnalysisPage(1, "Rent is 100 USD", extraction_id, "text")],
		settings(),
	)
	assert result.facts[0].value == "100 USD"
	assert client.calls == 1


@pytest.mark.asyncio
async def test_openai_provider_rejects_invalid_or_missing_evidence_output() -> None:
	document_id, extraction_id = uuid4(), uuid4()
	invalid_json = '{"classification":{"primary_type":"contract","explanation":"x"},"facts":[{"fact_type":"x","value":"y","classification":"SOURCE_FACT"}]}'
	provider = OpenAIProvider(settings(), client=FakeOpenAIClient(content=invalid_json))
	with pytest.raises(ProviderOutputError):
		await provider.analyze(document_id, [AnalysisPage(1, "source", extraction_id, "text")], settings())

	result = valid_result(document_id, extraction_id)
	result.facts[0].evidence[0].source_text = "not in source"
	page = DocumentPage(
		id=uuid4(), document_id=document_id, page_number=1, extracted_text="Rent is 100 USD",
		extraction_method="text", created_at=datetime.now(timezone.utc),
	)
	with pytest.raises(ValueError):
		validate_evidence(result, document_id, extraction_id, [page])


class APITimeoutError(Exception):
	pass


class AuthenticationError(Exception):
	pass


@pytest.mark.asyncio
async def test_openai_provider_normalizes_timeout_and_authentication_failures() -> None:
	document_id, extraction_id = uuid4(), uuid4()
	timeout_client = FakeOpenAIClient(error=APITimeoutError())
	provider = OpenAIProvider(settings(), client=timeout_client)
	with pytest.raises(ProviderUnavailableError, match="request failed"):
		await provider.analyze(document_id, [AnalysisPage(1, "source", extraction_id, "text")], settings())
	auth_client = FakeOpenAIClient(error=AuthenticationError())
	provider = OpenAIProvider(settings(), client=auth_client)
	with pytest.raises(ProviderUnavailableError, match="authentication failed"):
		await provider.analyze(document_id, [AnalysisPage(1, "source", extraction_id, "text")], settings())


def test_provider_selection_requires_configuration() -> None:
	with pytest.raises(ProviderUnavailableError, match="API key"):
		provider_from_settings(Settings(ANALYSIS_PROVIDER="openai", OPENAI_API_KEY="", OPENAI_MODEL="model"))
	with pytest.raises(ValueError, match="Unsupported"):
		Settings(ANALYSIS_PROVIDER="unknown")


class ExternalProviderProbe:
	identifier = "openai"
	model_name = "test-model"

	async def analyze(self, document_id, pages: Sequence[AnalysisPage], settings: Settings) -> AnalysisResult:
		return valid_result(document_id, pages[0].extraction_id)


@pytest.mark.asyncio
async def test_analysis_uses_configured_external_provider() -> None:
	engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
	factory = async_sessionmaker(engine, expire_on_commit=False)
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)
	document_id, user_id, extraction_id = uuid4(), uuid4(), uuid4()
	now = datetime.now(timezone.utc)
	async with factory() as session:
		document = Document(
			id=document_id, user_id=user_id, original_filename="notice.txt", storage_key="x", mime_type="text/plain",
			file_size=16, sha256_hash="d" * 64, document_type="txt", created_at=now, updated_at=now,
		)
		session.add_all([
			document,
			DocumentExtraction(
				id=extraction_id, user_id=user_id, document_id=document_id, extractor_type="text",
				extractor_version="test", processing_version="stage2-v1", status="completed", created_at=now,
			),
			DocumentPage(
				id=uuid4(), document_id=document_id, page_number=1, extracted_text="Rent is 100 USD",
				extraction_method="text", created_at=now,
			),
		])
		await session.commit()
		analysis = await analyze_document(session, document, settings(), ExternalProviderProbe())
		assert analysis.status == "completed"
		assert analysis.provider_identifier == "openai"
	await engine.dispose()
