# ORVEXA Master Codebase Audit

Audit type: Read-only static repository inspection
Project: `C:\My Projects\ORVEXA`
Audit date: 2026-11-09 01:26:28

> IMPORTANT: This report is generated from repository inspection. File presence does not prove runtime functionality. Unverified items must be checked separately.

## 1. Audit Safety

- No database connection was initiated by this script.
- No database migrations were executed.
- No application source files were modified by this script.
- `nova_health` was not accessed.
- One audit report file is created or overwritten: `docs/ORVEXA_MASTER_AUDIT.md`.


## 2. Project Inventory

- Total discovered files: 258
- Relevant source/configuration/documentation files: 147

### Top-level project entries
- .git [Directory]
- .pytest_cache [Directory]
- .vs [Directory]
- backend [Directory]
- docs [Directory]
- frontend [Directory]
- ORVEXA [Directory]
- .env.example [File]
- .gitignore [File]
- docker-compose.override.yml.example [File]
- docker-compose.yml [File]
- ORVEXA.slnx [File]
- README.md [File]

## 3. FastAPI / Python Backend Files

- `backend\alembic.ini`
- `backend\audit_http_auth.py`
- `backend\audit_runtime_auth.py`
- `backend\pyproject.toml`
- `backend\requirements.txt`
- `backend\app\main.py`
- `backend\app\phase3_models.py`
- `backend\app\__init__.py`
- `backend\app\api\__init__.py`
- `backend\app\api\v1\dependencies.py`
- `backend\app\api\v1\router.py`
- `backend\app\api\v1\endpoints\admin.py`
- `backend\app\api\v1\endpoints\auth.py`
- `backend\app\api\v1\endpoints\context.py`
- `backend\app\api\v1\endpoints\documents.py`
- `backend\app\api\v1\endpoints\intelligence.py`
- `backend\app\api\v1\endpoints\system.py`
- `backend\app\api\v1\endpoints\users.py`
- `backend\app\core\config.py`
- `backend\app\core\errors.py`
- `backend\app\core\exceptions.py`
- `backend\app\core\jwt.py`
- `backend\app\core\logging.py`
- `backend\app\core\rate_limit.py`
- `backend\app\core\security.py`
- `backend\app\core\__init__.py`
- `backend\app\database\base.py`
- `backend\app\database\domain_models.py`
- `backend\app\database\models.py`
- `backend\app\database\session.py`
- `backend\app\database\__init__.py`
- `backend\app\modules\__init__.py`
- `backend\app\modules\actions\models.py`
- `backend\app\modules\actions\policies.py`
- `backend\app\modules\actions\repositories.py`
- `backend\app\modules\actions\schemas.py`
- `backend\app\modules\actions\services.py`
- `backend\app\modules\actions\__init__.py`
- `backend\app\modules\documents\analysis_models.py`
- `backend\app\modules\documents\document_models.py`
- `backend\app\modules\documents\document_schemas.py`
- `backend\app\modules\documents\document_service.py`
- `backend\app\modules\documents\foo.txt`
- `backend\app\modules\documents\repositories.py`
- `backend\app\modules\documents\storage.py`
- `backend\app\modules\documents\validation.py`
- `backend\app\modules\documents\__init__.py`
- `backend\app\modules\evidence\models.py`
- `backend\app\modules\evidence\schemas.py`
- `backend\app\modules\evidence\__init__.py`
- `backend\app\modules\extraction\extractors.py`
- `backend\app\modules\extraction\models.py`
- `backend\app\modules\extraction\schemas.py`
- `backend\app\modules\extraction\service.py`
- `backend\app\modules\extraction\__init__.py`
- `backend\app\modules\intelligence\analysis_service.py`
- `backend\app\modules\intelligence\context_models.py`
- `backend\app\modules\intelligence\context_schemas.py`
- `backend\app\modules\intelligence\context_service.py`
- `backend\app\modules\intelligence\models.py`
- `backend\app\modules\intelligence\provider.py`
- `backend\app\modules\intelligence\schemas.py`
- `backend\app\modules\intelligence\stage3_schemas.py`
- `backend\app\modules\intelligence\__init__.py`
- `backend\app\schemas\auth.py`
- `backend\app\schemas\system.py`
- `backend\app\services\auth.py`
- `backend\app\shared\enums.py`
- `backend\app\shared\errors.py`
- `backend\app\shared\pagination.py`
- `backend\app\shared\timestamps.py`
- `backend\app\shared\__init__.py`
- `backend\app\workers\document_worker.py`
- `backend\app\workers\__init__.py`
- `backend\migrations\env.py`
- `backend\migrations\versions\0001_phase2_auth.py`
- `backend\migrations\versions\0002_phase3_documents.py`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py`
- `backend\migrations\versions\0004_document_lifecycle.py`
- `backend\migrations\versions\0005_document_extractions.py`
- `backend\migrations\versions\0006_stage2_extraction_jobs.py`
- `backend\migrations\versions\0007_stage3_document_analysis.py`
- `backend\migrations\versions\0008_stage4_context_privacy.py`
- `backend\tests\test_auth_security.py`
- `backend\tests\test_documents_api.py`
- `backend\tests\test_health.py`
- `backend\tests\test_phase2_migration.py`
- `backend\tests\test_stage1b_domain.py`
- `backend\tests\test_stage2_documents.py`
- `backend\tests\test_stage3_extraction.py`
- `backend\tests\test_stage3_intelligence.py`
- `backend\tests\__init__.py`

## 4. Flutter / Dart Files

- `frontend\pubspec.yaml`
- `frontend\lib\main.dart`
- `frontend\lib\app\app.dart`
- `frontend\lib\app\providers\theme_provider.dart`
- `frontend\lib\app\router\app_router.dart`
- `frontend\lib\core\config\app_config.dart`
- `frontend\lib\core\network\api_client.dart`
- `frontend\lib\core\theme\app_theme.dart`
- `frontend\lib\core\widgets\error_view.dart`
- `frontend\lib\core\widgets\loading_view.dart`
- `frontend\lib\features\documents\data\analysis.dart`
- `frontend\lib\features\documents\data\document.dart`
- `frontend\lib\features\documents\data\documents_api.dart`
- `frontend\lib\features\documents\presentation\documents_screen.dart`
- `frontend\lib\features\documents\presentation\document_detail_screen.dart`
- `frontend\lib\features\home\presentation\home_screen.dart`
- `frontend\lib\features\settings\presentation\settings_screen.dart`
- `frontend\test\api_client_test.dart`
- `frontend\test\app_test.dart`
- `frontend\test\widget_test.dart`

## 5. Database and Migration Files

- `backend\alembic.ini`
- `backend\migrations\env.py`
- `backend\migrations\versions\0001_phase2_auth.py`
- `backend\migrations\versions\0002_phase3_documents.py`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py`
- `backend\migrations\versions\0004_document_lifecycle.py`
- `backend\migrations\versions\0005_document_extractions.py`
- `backend\migrations\versions\0006_stage2_extraction_jobs.py`
- `backend\migrations\versions\0007_stage3_document_analysis.py`
- `backend\migrations\versions\0008_stage4_context_privacy.py`
- `backend\tests\test_phase2_migration.py`

## 6. Test Files

- `backend\tests\test_auth_security.py`
- `backend\tests\test_documents_api.py`
- `backend\tests\test_health.py`
- `backend\tests\test_phase2_migration.py`
- `backend\tests\test_stage1b_domain.py`
- `backend\tests\test_stage2_documents.py`
- `backend\tests\test_stage3_extraction.py`
- `backend\tests\test_stage3_intelligence.py`
- `backend\tests\__init__.py`
- `frontend\test\api_client_test.dart`
- `frontend\test\app_test.dart`
- `frontend\test\widget_test.dart`

## 7. Existing Documentation

- `README.md`
- `docs\AI_PIPELINE.md`
- `docs\API_DOCUMENTATION.md`
- `docs\ARCHITECTURE.md`
- `docs\AUTHENTICATION_FLOW.md`
- `docs\DATABASE_DESIGN.md`
- `docs\DEPLOYMENT.md`
- `docs\DEVELOPMENT_ENVIRONMENT_SETUP.md`
- `docs\ENVIRONMENT_DIAGNOSTIC_REPORT.md`
- `docs\ENVIRONMENT_REPORT.md`
- `docs\IMPLEMENTATION_PROGRESS.md`
- `docs\ORVEXA_MASTER_AUDIT.md`
- `docs\PHASE_1_VERIFICATION_REPORT.md`
- `docs\PHASE_2_IMPLEMENTATION_PLAN.md`
- `docs\PHASE_2_VERIFICATION_REPORT.md`
- `docs\PROJECT_OVERVIEW.md`
- `docs\PROJECT_SETUP.md`
- `docs\RESEARCH_METHODOLOGY.md`
- `docs\ROADMAP.md`
- `docs\SECURITY.md`
- `docs\SRS.md`
- `docs\STAGE1_IMPLEMENTATION_REPORT.md`
- `docs\TESTING.md`
- `docs\USER_GUIDE.md`
- `docs\architecture\stage-1-domain-foundation.md`
- `frontend\README.md`
- `frontend\ios\Runner\Assets.xcassets\LaunchImage.imageset\README.md`

## 8. Git Repository Status

- ## No commits yet on master
- ?? .env.example
- ?? .gitignore
- ?? ORVEXA.slnx
- ?? ORVEXA/
- ?? README.md
- ?? backend/
- ?? docker-compose.override.yml.example
- ?? docker-compose.yml
- ?? docs/
- ?? frontend/

## 9. Backend and Frontend Implementation Evidence

- `README.md` : line 16 — `Not implemented yet: authentication, database migrations/models, file uploads, OCR, AI providers, URL verification, actions, knowledge storage, offline sync, and production deployment.`
- `README.md` : line 30 — `4. Run backend tests: `python -m pytest backend/tests -q`.`
- `backend\audit_runtime_auth.py` : line 7 — `from app.core.jwt import decode_access_token`
- `backend\audit_runtime_auth.py` : line 39 — `ok(payload['type'] == 'access' and payload['sub'], 'JWT has validated access type and subject')`
- `backend\audit_runtime_auth.py` : line 41 — `ok(user.password_hash.startswith('$argon2id$'), 'database password hash is Argon2id')`
- `backend\audit_runtime_auth.py` : line 48 — `ok(r.status_code == 200, 'valid JWT reaches protected endpoint')`
- `backend\audit_runtime_auth.py` : line 50 — `ok(r.status_code == 401, 'tampered JWT is rejected')`
- `backend\pyproject.toml` : line 1 — `[tool.pytest.ini_options]`
- `backend\app\main.py` : line 13 — `app = FastAPI(`
- `backend\app\api\v1\dependencies.py` : line 10 — `from app.core.jwt import decode_access_token`
- `backend\app\api\v1\router.py` : line 10 — `api_router = APIRouter()`
- `backend\app\api\v1\endpoints\admin.py` : line 6 — `router = APIRouter(prefix="/admin", tags=["admin"])`
- `backend\app\api\v1\endpoints\admin.py` : line 9 — `@router.get("/example")`
- `backend\app\api\v1\endpoints\auth.py` : line 21 — `router = APIRouter(prefix="/auth", tags=["authentication"])`
- `backend\app\api\v1\endpoints\auth.py` : line 33 — `@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)`
- `backend\app\api\v1\endpoints\auth.py` : line 66 — `@router.post("/login", response_model=TokenResponse)`
- `backend\app\api\v1\endpoints\auth.py` : line 93 — `@router.post("/refresh", response_model=TokenResponse)`
- `backend\app\api\v1\endpoints\auth.py` : line 110 — `@router.post("/logout")`
- `backend\app\api\v1\endpoints\auth.py` : line 123 — `@router.post("/logout-all")`
- `backend\app\api\v1\endpoints\auth.py` : line 137 — `@router.get("/me", response_model=UserResponse)`
- `backend\app\api\v1\endpoints\context.py` : line 13 — `from app.modules.intelligence.context_models import ContextPreference, InsightEvidence, UserContext`
- `backend\app\api\v1\endpoints\context.py` : line 27 — `router = APIRouter(tags=["context", "insights"])`
- `backend\app\api\v1\endpoints\context.py` : line 51 — `@router.get("/context", response_model=list[ContextResponse])`
- `backend\app\api\v1\endpoints\context.py` : line 64 — `@router.post("/context", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)`
- `backend\app\api\v1\endpoints\context.py` : line 70 — `if payload.evidence_reference and payload.context_type not in {`
- `backend\app\api\v1\endpoints\context.py` : line 74 — `raise HTTPException(status_code=422, detail="Evidence-linked context must be document-derived or confirmed")`
- `backend\app\api\v1\endpoints\context.py` : line 86 — `@router.get("/context/{context_id}", response_model=ContextResponse)`
- `backend\app\api\v1\endpoints\context.py` : line 95 — `@router.patch("/context/{context_id}", response_model=ContextResponse)`
- `backend\app\api\v1\endpoints\context.py` : line 112 — `@router.delete("/context/{context_id}", status_code=status.HTTP_204_NO_CONTENT)`
- `backend\app\api\v1\endpoints\context.py` : line 124 — `@router.post("/context/{context_id}/confirm", response_model=ContextResponse)`
- `backend\app\api\v1\endpoints\context.py` : line 138 — `@router.post("/context/{context_id}/reject", response_model=ContextResponse)`
- `backend\app\api\v1\endpoints\context.py` : line 152 — `@router.get("/context/preferences", response_model=ContextPreferenceResponse)`
- `backend\app\api\v1\endpoints\context.py` : line 159 — `@router.patch("/context/preferences", response_model=ContextPreferenceResponse)`
- `backend\app\api\v1\endpoints\context.py` : line 173 — `@router.get("/context/relevant", response_model=list[ContextResponse])`
- `backend\app\api\v1\endpoints\context.py` : line 184 — `evidence_ids = list(`
- `backend\app\api\v1\endpoints\context.py` : line 185 — `await db.scalars(select(InsightEvidence.evidence_source_id).where(InsightEvidence.insight_id == insight.id))`
- `backend\app\api\v1\endpoints\context.py` : line 193 — `confidence=insight.confidence,`
- `backend\app\api\v1\endpoints\context.py` : line 196 — `evidence_source_ids=evidence_ids,`
- `backend\app\api\v1\endpoints\context.py` : line 201 — `@router.get("/insights", response_model=list[InsightResponse])`
- `backend\app\api\v1\endpoints\context.py` : line 209 — `@router.post("/insights/generate", response_model=InsightGenerationResponse)`
- `backend\app\api\v1\endpoints\context.py` : line 216 — `evidence_ids = [row.evidence_reference for row in context if row.evidence_reference and row.confirmation_status == "confirmed"]`
- `backend\app\api\v1\endpoints\context.py` : line 217 — `if not evidence_ids:`
- `backend\app\api\v1\endpoints\context.py` : line 220 — `limitation="No confirmed evidence-linked context is available for this request.",`
- `backend\app\api\v1\endpoints\context.py` : line 231 — `title="Evidence-backed personal context",`
- `backend\app\api\v1\endpoints\context.py` : line 234 — `confidence=1.0,`
- `backend\app\api\v1\endpoints\context.py` : line 239 — `for evidence_id in dict.fromkeys(evidence_ids):`
- `backend\app\api\v1\endpoints\context.py` : line 240 — `db.add(InsightEvidence(user_id=user.id, insight_id=insight.id, evidence_source_id=evidence_id))`
- `backend\app\api\v1\endpoints\context.py` : line 246 — `@router.post("/insights/{insight_id}/feedback", status_code=status.HTTP_201_CREATED)`
- `backend\app\api\v1\endpoints\documents.py` : line 3 — `from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status`
- `backend\app\api\v1\endpoints\documents.py` : line 16 — `from app.modules.extraction.extractors import available_ocr_languages`
- `backend\app\api\v1\endpoints\documents.py` : line 19 — `router = APIRouter(prefix="/documents", tags=["documents"])`
- `backend\app\api\v1\endpoints\documents.py` : line 26 — `@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)`
- `backend\app\api\v1\endpoints\documents.py` : line 28 — `file: UploadFile = File(...),`
- `backend\app\api\v1\endpoints\documents.py` : line 42 — `@router.get("", response_model=DocumentListResponse)`
- `backend\app\api\v1\endpoints\documents.py` : line 55 — `@router.get("/search", response_model=DocumentSearchResponse)`
- `backend\app\api\v1\endpoints\documents.py` : line 75 — `@router.get("/capabilities")`
- `backend\app\api\v1\endpoints\documents.py` : line 84 — `**available_ocr_languages(),`
- `backend\app\api\v1\endpoints\documents.py` : line 88 — `@router.get("/{document_id}", response_model=DocumentResponse)`
- `backend\app\api\v1\endpoints\documents.py` : line 96 — `@router.post("/{document_id}/extract", response_model=ProcessingJobResponse, status_code=status.HTTP_202_ACCEPTED)`
- `backend\app\api\v1\endpoints\documents.py` : line 105 — `@router.get("/{document_id}/extraction", response_model=ExtractionResponse)`
- `backend\app\api\v1\endpoints\documents.py` : line 121 — `@router.get("/{document_id}/pages", response_model=list[ExtractedPageResponse])`
- `backend\app\api\v1\endpoints\documents.py` : line 130 — `extraction_status=row.extraction_status, ocr_used=row.ocr_used,`
- `backend\app\api\v1\endpoints\documents.py` : line 131 — `error_summary=row.error_summary, extraction_confidence=row.extraction_confidence,`
- `backend\app\api\v1\endpoints\documents.py` : line 135 — `@router.get("/{document_id}/content")`
- `backend\app\api\v1\endpoints\documents.py` : line 146 — `@router.post("/{document_id}/archive", response_model=DocumentResponse)`
- `backend\app\api\v1\endpoints\documents.py` : line 154 — `@router.post("/{document_id}/retry", response_model=ProcessingJobResponse)`
- `backend\app\api\v1\endpoints\documents.py` : line 162 — `@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 24 — `EvidenceCollectionResponse,`
- `backend\app\api\v1\endpoints\intelligence.py` : line 25 — `EvidenceReference,`
- `backend\app\api\v1\endpoints\intelligence.py` : line 28 — `router = APIRouter(tags=["intelligence"])`
- `backend\app\api\v1\endpoints\intelligence.py` : line 64 — `@router.post("/documents/{document_id}/analyze", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 78 — `@router.get("/documents/{document_id}/analysis", response_model=AnalysisResponse)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 95 — `@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 104 — `@router.post("/analyses/{analysis_id}/retry", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 125 — `@router.get("/analyses/{analysis_id}/facts", response_model=AnalysisItemsResponse)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 130 — `@router.get("/analyses/{analysis_id}/dates", response_model=AnalysisItemsResponse)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 135 — `@router.get("/analyses/{analysis_id}/obligations", response_model=AnalysisItemsResponse)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 140 — `@router.get("/analyses/{analysis_id}/requirements", response_model=AnalysisItemsResponse)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 145 — `@router.get("/analyses/{analysis_id}/risks", response_model=AnalysisItemsResponse)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 150 — `@router.get("/analyses/{analysis_id}/evidence", response_model=EvidenceCollectionResponse)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 151 — `async def evidence(analysis_id: UUID, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> EvidenceCollectionResponse:`
- `backend\app\api\v1\endpoints\intelligence.py` : line 154 — `references: list[EvidenceReference] = list(result.classification.evidence)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 157 — `references.extend(item.evidence)`
- `backend\app\api\v1\endpoints\intelligence.py` : line 158 — `return EvidenceCollectionResponse(items=references[offset : offset + limit], total=len(references))`
- `backend\app\api\v1\endpoints\system.py` : line 10 — `router = APIRouter(tags=["system"])`
- `backend\app\api\v1\endpoints\system.py` : line 13 — `@router.get("/", response_model=RootResponse)`
- `backend\app\api\v1\endpoints\system.py` : line 24 — `@router.get("/health", response_model=HealthResponse)`
- `backend\app\api\v1\endpoints\system.py` : line 42 — `@router.get("/ready", response_model=ReadinessResponse)`
- `backend\app\api\v1\endpoints\users.py` : line 11 — `router = APIRouter(prefix="/users", tags=["users"])`
- `backend\app\api\v1\endpoints\users.py` : line 14 — `@router.get("/me", response_model=UserResponse)`
- `backend\app\api\v1\endpoints\users.py` : line 15 — `async def get_profile(user: User = Depends(get_current_user)) -> UserResponse:`
- `backend\app\api\v1\endpoints\users.py` : line 19 — `@router.patch("/me", response_model=UserResponse)`
- `backend\app\api\v1\endpoints\users.py` : line 20 — `async def update_profile(`
- `backend\app\core\config.py` : line 26 — `jwt_secret_key: SecretStr = Field(`
- `backend\app\core\config.py` : line 27 — `default=SecretStr("CHANGE_ME"), validation_alias="JWT_SECRET_KEY"`
- `backend\app\core\config.py` : line 29 — `jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")`
- `backend\app\core\config.py` : line 70 — `tesseract_cmd: str | None = Field(default=None, validation_alias="TESSERACT_CMD")`
- `backend\app\core\config.py` : line 72 — `ocr_default_lang: str = Field(default="eng", validation_alias="OCR_DEFAULT_LANG")`
- `backend\app\core\config.py` : line 73 — `ocr_supported_languages: str = Field(default="eng,sin,tam", validation_alias="OCR_SUPPORTED_LANGUAGES")`
- `backend\app\core\config.py` : line 74 — `ocr_timeout_seconds: int = Field(default=60, validation_alias="OCR_TIMEOUT_SECONDS")`
- `backend\app\core\config.py` : line 75 — `ocr_max_image_pixels: int = Field(default=25_000_000, validation_alias="OCR_MAX_IMAGE_PIXELS")`
- `backend\app\core\config.py` : line 87 — `@field_validator("jwt_algorithm")`
- `backend\app\core\config.py` : line 89 — `def validate_jwt_algorithm(cls, value: str) -> str:`
- `backend\app\core\config.py` : line 91 — `raise ValueError("Unsupported JWT algorithm")`
- `backend\app\core\config.py` : line 97 — `jwt_secret = self.jwt_secret_key.get_secret_value()`
- `backend\app\core\config.py` : line 98 — `if jwt_secret in {"", "CHANGE_ME"} or len(jwt_secret) < 32:`
- `backend\app\core\config.py` : line 99 — `raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production")`
- `backend\app\core\config.py` : line 109 — `def configured_ocr_languages(self) -> list[str]:`
- `backend\app\core\config.py` : line 110 — `return [language.strip() for language in self.ocr_supported_languages.split(",") if language.strip()]`
- `backend\app\core\jwt.py` : line 4 — `import jwt`
- `backend\app\core\jwt.py` : line 23 — `return jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)`
- `backend\app\core\jwt.py` : line 29 — `payload = jwt.decode(`
- `backend\app\core\jwt.py` : line 31 — `settings.jwt_secret_key.get_secret_value(),`
- `backend\app\core\jwt.py` : line 32 — `algorithms=[settings.jwt_algorithm],`
- `backend\app\core\jwt.py` : line 35 — `except jwt.PyJWTError as exc:`
- `backend\app\core\security.py` : line 5 — `from argon2 import PasswordHasher`
- `backend\app\core\security.py` : line 6 — `from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError`
- `backend\app\database\base.py` : line 1 — `from sqlalchemy.orm import DeclarativeBase`
- `backend\app\database\base.py` : line 3 — `class Base(DeclarativeBase):`
- `backend\app\database\domain_models.py` : line 2 — `from app.modules.evidence import models as evidence_models  # noqa: F401`
- `backend\app\database\domain_models.py` : line 6 — `__all__ = ["action_models", "evidence_models", "intelligence_models", "context_models"]`
- `backend\app\database\session.py` : line 6 — `from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine`
- `backend\app\database\session.py` : line 12 — `engine = create_async_engine(settings.get_database_url(), echo=False, pool_pre_ping=True, pool_size=5, max_overflow=5, connect_args={'timeout': settings.database_connect_timeout})`
- `backend\app\database\session.py` : line 13 — `SessionLocal = async_sessionmaker(engine, expire_on_commit=False)`
- `backend\app\modules\actions\models.py` : line 12 — `class Task(Base):`
- `backend\app\modules\actions\models.py` : line 16 — `Index("ix_tasks_action_plan_id", "action_plan_id"),`
- `backend\app\modules\actions\models.py` : line 22 — `action_plan_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("action_plans.id", ondelete="RESTRICT"))`
- `backend\app\modules\actions\models.py` : line 35 — `class TaskDependency(Base):`
- `backend\app\modules\actions\models.py` : line 50 — `class Goal(Base):`
- `backend\app\modules\actions\models.py` : line 65 — `class GoalMilestone(Base):`
- `backend\app\modules\actions\repositories.py` : line 9 — `class TaskRepository:`
- `backend\app\modules\actions\schemas.py` : line 4 — `from pydantic import BaseModel, Field, model_validator`
- `backend\app\modules\actions\schemas.py` : line 9 — `class TaskCreate(BaseModel):`
- `backend\app\modules\actions\schemas.py` : line 10 — `action_plan_id: UUID | None = None`
- `backend\app\modules\actions\schemas.py` : line 19 — `class TaskStatusUpdate(BaseModel):`
- `backend\app\modules\actions\schemas.py` : line 23 — `class TaskDependencyCreate(BaseModel):`
- `backend\app\modules\actions\schemas.py` : line 34 — `class GoalCreate(BaseModel):`
- `backend\app\modules\actions\schemas.py` : line 40 — `class GoalMilestoneCreate(BaseModel):`
- `backend\app\modules\actions\schemas.py` : line 47 — `class ActionPlanContract(BaseModel):`
- `backend\app\modules\actions\schemas.py` : line 51 — `class GoalStatusContract(BaseModel):`
- `backend\app\modules\actions\services.py` : line 39 — `class TaskService:`
- `backend\app\modules\documents\analysis_models.py` : line 39 — `confidence: Mapped[float | None] = mapped_column()`
- `backend\app\modules\documents\analysis_models.py` : line 52 — `evidence_text: Mapped[str | None] = mapped_column(Text)`
- `backend\app\modules\documents\analysis_models.py` : line 53 — `confidence: Mapped[float | None] = mapped_column()`
- `backend\app\modules\documents\analysis_models.py` : line 58 — `__tablename__ = 'action_plans'`
- `backend\app\modules\documents\analysis_models.py` : line 59 — `__table_args__ = (Index('ix_action_plans_user_id', 'user_id'),)`
- `backend\app\modules\documents\analysis_models.py` : line 70 — `__table_args__ = (Index('ix_actions_user_id', 'user_id'), Index('ix_actions_action_plan_id', 'action_plan_id'))`
- `backend\app\modules\documents\analysis_models.py` : line 74 — `action_plan_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('action_plans.id', ondelete='CASCADE'), nullable=False)`
- `backend\app\modules\documents\analysis_models.py` : line 80 — `evidence_reference: Mapped[dict | None] = mapped_column(JSON)`
- `backend\app\modules\documents\analysis_models.py` : line 81 — `confidence: Mapped[float | None] = mapped_column()`
- `backend\app\modules\documents\document_models.py` : line 42 — `ocr_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)`
- `backend\app\modules\documents\document_models.py` : line 44 — `extraction_confidence: Mapped[float | None] = mapped_column()`
- `backend\app\modules\documents\document_schemas.py` : line 4 — `from pydantic import BaseModel, ConfigDict, Field`
- `backend\app\modules\documents\document_schemas.py` : line 7 — `class DocumentResponse(BaseModel):`
- `backend\app\modules\documents\document_schemas.py` : line 22 — `class DocumentSearchResponse(BaseModel):`
- `backend\app\modules\documents\document_schemas.py` : line 29 — `class DocumentListResponse(BaseModel):`
- `backend\app\modules\documents\document_schemas.py` : line 36 — `class ProcessingJobResponse(BaseModel):`
- `backend\app\modules\evidence\models.py` : line 12 — `class EvidenceSource(Base):`
- `backend\app\modules\evidence\models.py` : line 13 — `__tablename__ = "evidence_sources"`
- `backend\app\modules\evidence\models.py` : line 15 — `Index("ix_evidence_sources_user_id", "user_id"),`
- `backend\app\modules\evidence\models.py` : line 16 — `CheckConstraint("document_id IS NOT NULL OR analysis_run_id IS NOT NULL", name="ck_evidence_source_parent"),`
- `backend\app\modules\evidence\models.py` : line 24 — `source_reference: Mapped[str] = mapped_column(String(500), nullable=False)`
- `backend\app\modules\evidence\schemas.py` : line 3 — `from pydantic import BaseModel, Field, model_validator`
- `backend\app\modules\evidence\schemas.py` : line 8 — `class EvidenceSourceCreate(BaseModel):`
- `backend\app\modules\evidence\schemas.py` : line 12 — `source_reference: str = Field(min_length=1, max_length=500)`
- `backend\app\modules\evidence\schemas.py` : line 19 — `def require_parent(self) -> "EvidenceSourceCreate":`
- `backend\app\modules\evidence\schemas.py` : line 21 — `raise ValueError("An evidence source must reference a document or analysis run")`
- `backend\app\modules\extraction\extractors.py` : line 32 — `confidence: float | None = None`
- `backend\app\modules\extraction\extractors.py` : line 34 — `ocr_used: bool = False`
- `backend\app\modules\extraction\extractors.py` : line 76 — `def _tesseract_executable(settings: Settings) -> str | None:`
- `backend\app\modules\extraction\extractors.py` : line 77 — `return settings.tesseract_cmd or shutil.which("tesseract")`
- `backend\app\modules\extraction\extractors.py` : line 80 — `def available_ocr_languages(settings: Settings | None = None) -> dict[str, object]:`
- `backend\app\modules\extraction\extractors.py` : line 82 — `executable = _tesseract_executable(settings)`
- `backend\app\modules\extraction\extractors.py` : line 84 — `return {"available": False, "executable": None, "languages": [], "configured": settings.configured_ocr_languages}`
- `backend\app\modules\extraction\extractors.py` : line 88 — `timeout=settings.ocr_timeout_seconds,`
- `backend\app\modules\extraction\extractors.py` : line 91 — `return {"available": False, "executable": executable, "languages": [], "configured": settings.configured_ocr_languages}`
- `backend\app\modules\extraction\extractors.py` : line 97 — `"configured": settings.configured_ocr_languages,`
- `backend\app\modules\extraction\extractors.py` : line 101 — `class ImageOcrExtractor:`
- `backend\app\modules\extraction\extractors.py` : line 102 — `extractor_type = "tesseract"`
- `backend\app\modules\extraction\extractors.py` : line 107 — `self.language = language or self.settings.ocr_default_lang`
- `backend\app\modules\extraction\extractors.py` : line 113 — `executable = _tesseract_executable(self.settings)`
- `backend\app\modules\extraction\extractors.py` : line 115 — `raise CapabilityUnavailable("Tesseract is not installed or configured")`
- `backend\app\modules\extraction\extractors.py` : line 116 — `with tempfile.TemporaryDirectory(prefix="orvexa-ocr-") as directory:`
- `backend\app\modules\extraction\extractors.py` : line 125 — `timeout=self.settings.ocr_timeout_seconds,`
- `backend\app\modules\extraction\extractors.py` : line 128 — `raise ExtractionError("OCR timed out") from exc`
- `backend\app\modules\extraction\extractors.py` : line 130 — `raise CapabilityUnavailable("Tesseract is not installed or configured") from exc`
- `backend\app\modules\extraction\extractors.py` : line 134 — `raise CapabilityUnavailable("Configured OCR language data is unavailable") from exc`
- `backend\app\modules\extraction\extractors.py` : line 135 — `raise ExtractionError("OCR failed") from exc`
- `backend\app\modules\extraction\extractors.py` : line 136 — `return ExtractedPage(page_number, result.stdout.decode("utf-8", errors="replace"), self.extractor_type, ocr_used=True)`
- `backend\app\modules\extraction\extractors.py` : line 141 — `extractor_version = "pypdfium2-2"`
- `backend\app\modules\extraction\extractors.py` : line 148 — `from pypdf import PdfReader`
- `backend\app\modules\extraction\extractors.py` : line 150 — `raise CapabilityUnavailable("PDF extraction requires the pypdf dependency") from exc`
- `backend\app\modules\extraction\extractors.py` : line 163 — `pages.append(ImageOcrExtractor(settings=self.settings)._run(image, page_number))`
- `backend\app\modules\extraction\extractors.py` : line 167 — `pages.append(ExtractedPage(page_number, text, "ocr", status="failed", error_summary=str(exc)))`
- `backend\app\modules\extraction\extractors.py` : line 196 — `import pypdfium2 as pdfium`
- `backend\app\modules\extraction\extractors.py` : line 199 — `raise CapabilityUnavailable("PDF OCR rendering requires pypdfium2 and Pillow") from exc`
- `backend\app\modules\extraction\extractors.py` : line 206 — `max_pixels = (settings or get_settings()).ocr_max_image_pixels`
- `backend\app\modules\extraction\extractors.py` : line 220 — `class TesseractOcrExtractor:`
- `backend\app\modules\extraction\extractors.py` : line 221 — `extractor_type = "tesseract"`
- `backend\app\modules\extraction\extractors.py` : line 228 — `executable = shutil.which("tesseract")`
- `backend\app\modules\extraction\extractors.py` : line 230 — `raise CapabilityUnavailable("Tesseract is not installed")`
- `backend\app\modules\extraction\extractors.py` : line 242 — `raise ExtractionError("OCR timed out") from exc`
- `backend\app\modules\extraction\extractors.py` : line 245 — `raise ExtractionError(f"OCR failed: {message}") from exc`
- `backend\app\modules\extraction\extractors.py` : line 255 — `}.get(extension, ImageOcrExtractor())`
- `backend\app\modules\extraction\schemas.py` : line 4 — `from pydantic import BaseModel, ConfigDict`
- `backend\app\modules\extraction\schemas.py` : line 7 — `class ExtractionResponse(BaseModel):`
- `backend\app\modules\extraction\schemas.py` : line 24 — `class ExtractedPageResponse(BaseModel):`
- `backend\app\modules\extraction\schemas.py` : line 29 — `ocr_used: bool`
- `backend\app\modules\extraction\schemas.py` : line 31 — `extraction_confidence: float | None`
- `backend\app\modules\extraction\service.py` : line 50 — `ocr_used=page.ocr_used,`
- `backend\app\modules\extraction\service.py` : line 52 — `extraction_confidence=page.confidence, created_at=now,`
- `backend\app\modules\intelligence\analysis_service.py` : line 22 — `from app.modules.intelligence.stage3_schemas import AnalysisResult, AnalysisStatus, EvidenceReference, EvidenceValidationStatus`
- `backend\app\modules\intelligence\analysis_service.py` : line 29 — `class EvidenceValidationError(ValueError):`
- `backend\app\modules\intelligence\analysis_service.py` : line 54 — `reference: EvidenceReference,`
- `backend\app\modules\intelligence\analysis_service.py` : line 58 — `) -> EvidenceReference:`
- `backend\app\modules\intelligence\analysis_service.py` : line 60 — `raise EvidenceValidationError("Evidence references a different document or extraction")`
- `backend\app\modules\intelligence\analysis_service.py` : line 63 — `raise EvidenceValidationError("Evidence references a page that does not exist")`
- `backend\app\modules\intelligence\analysis_service.py` : line 68 — `raise EvidenceValidationError("Evidence offsets do not match extracted page text")`
- `backend\app\modules\intelligence\analysis_service.py` : line 70 — `raise EvidenceValidationError("Evidence text is not present on the referenced page")`
- `backend\app\modules\intelligence\analysis_service.py` : line 71 — `return reference.model_copy(update={"validation_status": EvidenceValidationStatus.validated})`
- `backend\app\modules\intelligence\analysis_service.py` : line 74 — `def validate_evidence(`
- `backend\app\modules\intelligence\analysis_service.py` : line 82 — `def references(items: Sequence[EvidenceReference]) -> list[EvidenceReference]:`
- `backend\app\modules\intelligence\analysis_service.py` : line 86 — `data["classification"]["evidence"] = references(result.classification.evidence)`
- `backend\app\modules\intelligence\analysis_service.py` : line 88 — `data[key] = [item.model_copy(update={"evidence": references(item.evidence)}).model_dump() for item in getattr(result, key)]`
- `backend\app\modules\intelligence\analysis_service.py` : line 142 — `result = validate_evidence(result, document.id, extraction.id, pages)`
- `backend\app\modules\intelligence\analysis_service.py` : line 156 — `except (EvidenceValidationError, ProviderOutputError, ValueError) as exc:`
- `backend\app\modules\intelligence\context_models.py` : line 27 — `source_reference: Mapped[str | None] = mapped_column(String(500))`
- `backend\app\modules\intelligence\context_models.py` : line 28 — `evidence_reference: Mapped[uuid.UUID | None] = mapped_column(`
- `backend\app\modules\intelligence\context_models.py` : line 29 — `Uuid, ForeignKey("evidence_sources.id", ondelete="RESTRICT")`
- `backend\app\modules\intelligence\context_models.py` : line 31 — `confidence: Mapped[str | None] = mapped_column(String(16))`
- `backend\app\modules\intelligence\context_models.py` : line 69 — `class InsightEvidence(Base):`
- `backend\app\modules\intelligence\context_models.py` : line 70 — `__tablename__ = "insight_evidence"`
- `backend\app\modules\intelligence\context_models.py` : line 72 — `Index("ix_insight_evidence_user_id", "user_id"),`
- `backend\app\modules\intelligence\context_models.py` : line 82 — `evidence_source_id: Mapped[uuid.UUID] = mapped_column(`
- `backend\app\modules\intelligence\context_models.py` : line 83 — `Uuid, ForeignKey("evidence_sources.id", ondelete="RESTRICT"), nullable=False`
- `backend\app\modules\intelligence\context_schemas.py` : line 7 — `from pydantic import BaseModel, ConfigDict, Field`
- `backend\app\modules\intelligence\context_schemas.py` : line 25 — `class ContextCreate(BaseModel):`
- `backend\app\modules\intelligence\context_schemas.py` : line 30 — `source_reference: str | None = Field(default=None, max_length=500)`
- `backend\app\modules\intelligence\context_schemas.py` : line 31 — `evidence_reference: UUID | None = None`
- `backend\app\modules\intelligence\context_schemas.py` : line 32 — `confidence: str | None = Field(default=None, max_length=16)`
- `backend\app\modules\intelligence\context_schemas.py` : line 38 — `class ContextUpdate(BaseModel):`
- `backend\app\modules\intelligence\context_schemas.py` : line 46 — `class ContextResponse(BaseModel):`
- `backend\app\modules\intelligence\context_schemas.py` : line 54 — `source_reference: str | None`
- `backend\app\modules\intelligence\context_schemas.py` : line 55 — `evidence_reference: UUID | None`
- `backend\app\modules\intelligence\context_schemas.py` : line 56 — `confidence: str | None`
- `backend\app\modules\intelligence\context_schemas.py` : line 67 — `class ContextPreferenceUpdate(BaseModel):`
- `backend\app\modules\intelligence\context_schemas.py` : line 74 — `class ContextPreferenceResponse(BaseModel):`
- `backend\app\modules\intelligence\context_schemas.py` : line 85 — `class InsightFeedbackCreate(BaseModel):`
- `backend\app\modules\intelligence\context_schemas.py` : line 90 — `class InsightResponse(BaseModel):`
- `backend\app\modules\intelligence\context_schemas.py` : line 96 — `confidence: float | None`
- `backend\app\modules\intelligence\context_schemas.py` : line 99 — `evidence_source_ids: list[UUID]`
- `backend\app\modules\intelligence\context_schemas.py` : line 103 — `class InsightGenerationResponse(BaseModel):`
- `backend\app\modules\intelligence\models.py` : line 72 — `CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="ck_insights_confidence_range"),`
- `backend\app\modules\intelligence\models.py` : line 83 — `confidence: Mapped[float | None] = mapped_column()`
- `backend\app\modules\intelligence\schemas.py` : line 5 — `from pydantic import BaseModel, ConfigDict, Field, field_validator`
- `backend\app\modules\intelligence\schemas.py` : line 10 — `class IntelligenceRequestCreate(BaseModel):`
- `backend\app\modules\intelligence\schemas.py` : line 16 — `class InsightCreate(BaseModel):`
- `backend\app\modules\intelligence\schemas.py` : line 22 — `confidence: float | None = Field(default=None, ge=0, le=1)`
- `backend\app\modules\intelligence\schemas.py` : line 26 — `class ContextReferenceCreate(BaseModel):`
- `backend\app\modules\intelligence\schemas.py` : line 32 — `class FeedbackCreate(BaseModel):`
- `backend\app\modules\intelligence\schemas.py` : line 38 — `class IntelligenceResponse(BaseModel):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 7 — `from pydantic import BaseModel, ConfigDict, Field, model_validator`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 28 — `class EvidenceValidationStatus(StrEnum):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 35 — `class ConfidenceLevel(StrEnum):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 42 — `class EvidenceReference(BaseModel):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 53 — `validation_status: EvidenceValidationStatus = EvidenceValidationStatus.pending`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 56 — `def validate_offsets(self) -> "EvidenceReference":`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 58 — `raise ValueError("Evidence end offset must not precede its start offset")`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 62 — `class ClassifiedItem(BaseModel):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 66 — `confidence: float | None = Field(default=None, ge=0, le=1)`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 67 — `confidence_level: ConfidenceLevel = ConfidenceLevel.unknown`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 69 — `evidence: list[EvidenceReference] = Field(min_length=1, max_length=20)`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 72 — `class DocumentClassification(BaseModel):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 77 — `confidence: float | None = Field(default=None, ge=0, le=1)`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 79 — `evidence: list[EvidenceReference] = Field(default_factory=list, max_length=20)`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 130 — `class AnalysisResult(BaseModel):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 154 — `class AnalysisResponse(BaseModel):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 171 — `class AnalysisRequestResponse(BaseModel):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 177 — `class EvidenceCollectionResponse(BaseModel):`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 178 — `items: list[EvidenceReference]`
- `backend\app\modules\intelligence\stage3_schemas.py` : line 182 — `class AnalysisItemsResponse(BaseModel):`
- `backend\app\schemas\auth.py` : line 4 — `from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator`
- `backend\app\schemas\auth.py` : line 9 — `class UserCreate(BaseModel):`
- `backend\app\schemas\auth.py` : line 24 — `class LoginRequest(BaseModel):`
- `backend\app\schemas\auth.py` : line 30 — `class RefreshRequest(BaseModel):`
- `backend\app\schemas\auth.py` : line 34 — `class UserResponse(BaseModel):`
- `backend\app\schemas\auth.py` : line 49 — `class TokenResponse(BaseModel):`
- `backend\app\schemas\auth.py` : line 57 — `class ProfileUpdate(BaseModel):`
- `backend\app\schemas\system.py` : line 3 — `from pydantic import BaseModel`
- `backend\app\schemas\system.py` : line 5 — `class RootResponse(BaseModel):`
- `backend\app\schemas\system.py` : line 11 — `class HealthResponse(BaseModel):`
- `backend\app\schemas\system.py` : line 17 — `class ReadinessResponse(BaseModel):`
- `backend\app\services\auth.py` : line 9 — `from app.core.jwt import create_access_token`
- `backend\app\shared\enums.py` : line 41 — `class ApprovalStatus(StrEnum):`
- `backend\app\shared\enums.py` : line 48 — `class TaskStatus(StrEnum):`
- `backend\app\shared\enums.py` : line 55 — `class GoalStatus(StrEnum):`
- `backend\app\shared\errors.py` : line 3 — `from pydantic import BaseModel`
- `backend\app\shared\errors.py` : line 16 — `class ErrorDetail(BaseModel):`
- `backend\app\shared\errors.py` : line 21 — `class ErrorResponse(BaseModel):`
- `backend\app\shared\pagination.py` : line 1 — `from pydantic import BaseModel, Field`
- `backend\app\shared\pagination.py` : line 4 — `class PaginationParams(BaseModel):`
- `backend\app\shared\pagination.py` : line 9 — `class Page[T](BaseModel):`
- `backend\app\workers\document_worker.py` : line 9 — `from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker`
- `backend\app\workers\document_worker.py` : line 103 — `session_factory: async_sessionmaker[AsyncSession], settings: Settings | None = None`
- `backend\app\workers\document_worker.py` : line 147 — `session_factory: async_sessionmaker[AsyncSession] = SessionLocal,`
- `backend\migrations\versions\0002_phase3_documents.py` : line 39 — `sa.Column('extraction_method', sa.String(32), nullable=False), sa.Column('extraction_confidence', sa.Float()),`
- `backend\migrations\versions\0002_phase3_documents.py` : line 56 — `sa.Column('confidence', sa.Float()), sa.Column('error_message', sa.Text()),`
- `backend\migrations\versions\0002_phase3_documents.py` : line 63 — `sa.Column('source_page', sa.Integer()), sa.Column('evidence_text', sa.Text()), sa.Column('confidence', sa.Float()),`
- `backend\migrations\versions\0002_phase3_documents.py` : line 67 — `op.create_table('action_plans',`
- `backend\migrations\versions\0002_phase3_documents.py` : line 72 — `op.create_index('ix_action_plans_user_id', 'action_plans', ['user_id'])`
- `backend\migrations\versions\0002_phase3_documents.py` : line 75 — `sa.Column('action_plan_id', sa.Uuid(), nullable=False), sa.Column('title', sa.String(200), nullable=False), sa.Column('description', sa.Text(), nullable=False),`
- `backend\migrations\versions\0002_phase3_documents.py` : line 77 — `sa.Column('evidence_reference', sa.JSON()), sa.Column('confidence', sa.Float()), sa.Column('approved_at', sa.DateTime(timezone=True)),`
- `backend\migrations\versions\0002_phase3_documents.py` : line 80 — `sa.ForeignKeyConstraint(['action_plan_id'], ['action_plans.id'], ondelete='CASCADE'), sa.PrimaryKeyConstraint('id'))`
- `backend\migrations\versions\0002_phase3_documents.py` : line 81 — `op.create_index('ix_actions_user_id', 'actions', ['user_id']); op.create_index('ix_actions_action_plan_id', 'actions', ['action_plan_id'])`
- `backend\migrations\versions\0002_phase3_documents.py` : line 85 — `op.drop_index('ix_actions_action_plan_id', table_name='actions'); op.drop_index('ix_actions_user_id', table_name='actions'); op.drop_table('actions')`
- `backend\migrations\versions\0002_phase3_documents.py` : line 86 — `op.drop_index('ix_action_plans_user_id', table_name='action_plans'); op.drop_table('action_plans')`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 66 — `sa.Column("confidence", sa.Float()),`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 70 — `sa.CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="ck_insights_confidence_range"),`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 108 — `"evidence_sources",`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 114 — `sa.Column("source_reference", sa.String(500), nullable=False),`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 120 — `sa.CheckConstraint("document_id IS NOT NULL OR analysis_run_id IS NOT NULL", name="ck_evidence_source_parent"),`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 126 — `op.create_index("ix_evidence_sources_user_id", "evidence_sources", ["user_id"])`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 148 — `sa.Column("action_plan_id", sa.Uuid()),`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 161 — `sa.ForeignKeyConstraint(["action_plan_id"], ["action_plans.id"], ondelete="RESTRICT"),`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 166 — `op.create_index("ix_tasks_action_plan_id", "tasks", ["action_plan_id"])`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 208 — `op.drop_index("ix_tasks_action_plan_id", table_name="tasks")`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 213 — `op.drop_index("ix_evidence_sources_user_id", table_name="evidence_sources")`
- `backend\migrations\versions\0003_stage1b_domain_foundation.py` : line 214 — `op.drop_table("evidence_sources")`
- `backend\migrations\versions\0006_stage2_extraction_jobs.py` : line 63 — `sa.Column("ocr_used", sa.Boolean(), nullable=False, server_default=sa.false()),`
- `backend\migrations\versions\0006_stage2_extraction_jobs.py` : line 70 — `op.drop_column("document_pages", "ocr_used")`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 1 — `"""Add privacy-aware personal context and insight evidence links.`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 26 — `sa.Column("source_reference", sa.String(500)),`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 27 — `sa.Column("evidence_reference", sa.Uuid()),`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 28 — `sa.Column("confidence", sa.String(16)),`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 38 — `sa.ForeignKeyConstraint(["evidence_reference"], ["evidence_sources.id"], ondelete="RESTRICT"),`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 57 — `"insight_evidence",`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 61 — `sa.Column("evidence_source_id", sa.Uuid(), nullable=False),`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 66 — `sa.ForeignKeyConstraint(["evidence_source_id"], ["evidence_sources.id"], ondelete="RESTRICT"),`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 68 — `sa.UniqueConstraint("insight_id", "evidence_source_id", name="uq_insight_evidence_link"),`
- `backend\migrations\versions\0008_stage4_context_privacy.py` : line 70 — `op.create_index("ix_insight_evidence_user_id", "insight_evidence", ["user_id"])`
- `backend\tests\test_auth_security.py` : line 1 — `import pytest`
- `backend\tests\test_auth_security.py` : line 13 — `def test_production_rejects_placeholder_jwt_secret() -> None:`
- `backend\tests\test_auth_security.py` : line 14 — `with pytest.raises(ValidationError):`
- `backend\tests\test_auth_security.py` : line 15 — `Settings(APP_ENV="production", JWT_SECRET_KEY="CHANGE_ME")`
- `backend\tests\test_auth_security.py` : line 18 — `def test_production_requires_a_strong_jwt_secret() -> None:`
- `backend\tests\test_auth_security.py` : line 19 — `with pytest.raises(ValidationError):`
- `backend\tests\test_auth_security.py` : line 20 — `Settings(APP_ENV="production", JWT_SECRET_KEY="too-short")`
- `backend\tests\test_auth_security.py` : line 23 — `def test_only_supported_jwt_algorithm_is_allowed() -> None:`
- `backend\tests\test_auth_security.py` : line 24 — `with pytest.raises(ValidationError):`
- `backend\tests\test_auth_security.py` : line 25 — `Settings(JWT_ALGORITHM="none")`

## 10. Configuration File Inventory


## Configuration Files

- `.gitignore`
- `docker-compose.yml`
- `backend\alembic.ini`
- `backend\Dockerfile`
- `backend\pyproject.toml`
- `backend\requirements.txt`
- `frontend\.gitignore`
- `frontend\pubspec.yaml`
- `frontend\android\.gitignore`
- `frontend\ios\.gitignore`

## 11. Product Workflow Status

| Workflow | Static inspection status |
|---|---|
| Information Input | Requires detailed source verification |
| Understand | Requires extraction/OCR/AI verification |
| Insight | Requires context and insight service verification |
| Decide | Requires decision and approval verification |
| Act | Requires execution and authorization verification |
| Track | Requires tasks, goals, reminders and persistence verification |

## 12. Database Runtime Verification

- PostgreSQL runtime connectivity: NOT VERIFIED
- Applied database migration revision: NOT VERIFIED by this script
- Table contents: NOT INSPECTED
- `nova_health`: NOT ACCESSED

## 13. AI and End-to-End Verification

- AI provider runtime: NOT VERIFIED
- Document-to-analysis workflow: NOT VERIFIED
- Flutter-to-FastAPI live integration: NOT VERIFIED
- Approval-to-action execution: NOT VERIFIED
- Full Understand → Insight → Decide → Act → Track workflow: NOT VERIFIED

## 14. Limitations

- This is a static inventory and keyword-based evidence collection.
- Matching a keyword does not prove that a feature works.
- Source code, tests and runtime behavior require further manual verification.
- No AI reasoning or semantic implementation review was performed by PowerShell.

## 15. Next Step

Review this report and verify the actual implementation files, API behavior, test coverage and safe runtime evidence before approving any implementation.

END OF READ-ONLY AUDIT REPORT
