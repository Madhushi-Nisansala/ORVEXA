# ORVEXA Stage 1 Domain Foundation

## Scope and safety status

This document records the Stage 1A inspection and the completed Stage 1B shared domain foundation.

Stage 1B added only new backend models, contracts, tests, documentation, and the forward-only `0003_stage1b_domain_foundation` migration. No connection was made to `nova_health`, and no existing migration or authentication table was modified. No downgrade or stamp was run.

The verified runtime database identity was `orvexa_db` using role `orvexa`; its Alembic revision was `0002_phase3_documents` before the approved additive upgrade. The migration was applied only to that database, and the post-upgrade head is `0003_stage1b_domain_foundation`.

## 1. Existing architecture summary

ORVEXA currently uses a modular-monolith direction with:

- A FastAPI backend under `backend/app`.
- SQLAlchemy 2.x asynchronous sessions and PostgreSQL/asyncpg configuration.
- Alembic migrations under `backend/migrations`.
- A Flutter client under `frontend` using Material 3, Riverpod, GoRouter, and Dio.
- An existing .NET 10 console baseline under `ORVEXA/`; this project is separate from the FastAPI and Flutter application and is preserved unchanged.

The backend currently exposes system, authentication, user, and administrative route areas. Authentication uses the existing `users`, `roles`, `user_roles`, and `refresh_tokens` entities. Backend dependencies and authentication behavior remain outside Stage 1A changes.

## 2. Verified source configuration

`backend/app/core/config.py` defines these non-secret database defaults:

- Database: `orvexa_db`
- User: `orvexa`
- Host: `localhost`
- Port: `5432`
- Driver: `postgresql+asyncpg`

A `DATABASE_URL` environment value can override the constructed URL. Passwords are held by `SecretStr` and were not printed. The repository `.env.example` contains a different example database name (`orvexa`); this is a configuration inconsistency that must be resolved from the actual runtime environment before any database operation.

`backend/alembic.ini` sets `script_location = migrations` and leaves the URL empty. `backend/migrations/env.py` obtains the URL from application settings and imports the authentication models and document models into Alembic metadata.

## 3. Verified migration source state

The repository contains this linear migration chain:

```text
0001_phase2_auth
	|
	v
0002_phase3_documents
	|
	v
0003_stage1b_domain_foundation
```

### `0001_phase2_auth`

Defines and seeds the Phase 2 authentication foundation:

- `users`
- `roles`
- `user_roles`
- `refresh_tokens`

It seeds the `user` and `admin` roles. This migration is protected and must not be edited.

### `0002_phase3_documents`

Defines source-level tables for:

- `documents`
- `document_pages`
- `document_processing_jobs`
- `analyses`
- `extracted_facts`
- `action_plans`
- `actions`

Its declared dependency is `0001_phase2_auth`. The migration contains foreign keys, indexes, and cascade/restrict behavior, but it does not represent the complete target domain for evidence, goals, tasks, reminders, feedback, or analysis history.

The live database was read-only verified before upgrade at `0002_phase3_documents`; the new migration was reviewed offline and applied to `orvexa_db`. `alembic current` now reports `0003_stage1b_domain_foundation`, and `alembic check` reports no remaining operations.

## 4. Existing reusable entities and models

The existing authentication models in `backend/app/database/models.py` are reusable and must not be duplicated:

- `User` is the root owner identity.
- `Role` and `user_roles` provide the current role boundary.
- `RefreshToken` owns authentication session state.

The repository also contains existing Phase 3 document and analysis models:

- `Document` and `DocumentPage` in `backend/app/modules/documents/document_models.py`.
- `DocumentProcessingJob`, `Analysis`, `ExtractedFact`, `ActionPlan`, and `Action` in `backend/app/modules/documents/analysis_models.py`.

These models are imported by `backend/migrations/env.py`, so Stage 1B must extend or correct them only after live schema verification. It must not create parallel document, analysis, or action entities.

Current model limitations to address only in a later approved stage include limited relationships between analysis/action models, no explicit evidence-source entity, no task/goal/reminder model, limited lifecycle constraints, and no complete audit/feedback model.

## 5. Proposed module boundaries

The existing modular monolith should be extended with explicit application boundaries:

```text
API endpoints
  -> application services
	-> domain policies and value types
	  -> repository interfaces
		-> SQLAlchemy repositories
```

### Personal Intelligence Core

Owns:

- Intelligence request intake and classification.
- Context assembly from authorized sources.
- Analysis-run coordination.
- Structured insights and recommendations.
- Confidence and uncertainty representation.
- Decision-support outputs.
- Analysis history and user feedback associations.

It must not directly own uploaded-file storage or task execution.

### Document Intelligence

Owns:

- Document metadata and lifecycle.
- Secure ingestion coordination.
- Processing jobs.
- Text/extraction results.
- Extracted facts.
- Evidence location and source references.
- Document analysis inputs and outputs.

It must treat document contents, extracted text, URLs, and provider responses as untrusted data.

### Action Engine

Owns:

- Proposed action candidates.
- Action plans, milestones, and tasks.
- Dependencies and status transitions.
- User approval and dismissal.
- Goals and progress relationships.
- Deadline/reminder coordination.

It must not execute consequential external actions without explicit authorization and confirmation.

### Shared boundaries

Shared contracts should contain only cross-cutting types such as:

- UUID and timestamp conventions.
- Pagination.
- Ownership context.
- Confidence and verification states.
- Evidence references.
- Safe error responses.
- Audit event contracts.

Provider abstractions should be separate from domain services:

- `StorageProvider`
- `DocumentExtractionProvider`
- `OCRProvider`
- `AIProvider` / structured text generation provider
- `MalwareScanner`
- `NotificationProvider`

Unconfigured providers must produce clear configuration errors, not fabricated production responses.

## 6. Proposed domain entities

These are design candidates, not authorization to create tables:

### Existing entities to reuse

- `User`
- `Role`
- `RefreshToken`
- `Document`
- `DocumentPage`
- `DocumentProcessingJob`
- `Analysis`
- `ExtractedFact`
- `ActionPlan`
- `Action`

### Potential additions after live-schema verification

- `EvidenceSource` — canonical source location and evidence text metadata.
- `AnalysisRun` — repeatable analysis execution history and provider status.
- `Insight` — evidence-aware fact, inference, uncertainty, or recommendation.
- `ActionPlanMilestone` — ordered plan milestone.
- `Task` — approved or proposed executable work item.
- `TaskDependency` — directed dependency between tasks.
- `Goal` and `GoalMilestone` — user-owned objectives and progress checkpoints.
- `Reminder` — user-approved reminder scheduling and delivery state.
- `UserFeedback` — explicit feedback tied to an analysis, insight, recommendation, or action.
- `ActivityEvent` — safe audit history for important state transitions.
- `UserPreference` or `UserMemoryItem` — only for explicitly approved persistent context.

The existing `Action` entity should be evaluated as the legacy/partial action-candidate concept before introducing a separate `Task`. A duplicate table must not be created without a documented compatibility decision.

## 7. Proposed relationships

The intended relationship graph is:

```text
User
 ├── Documents
 │    ├── ProcessingJobs
 │    ├── Pages / extraction results
 │    └── AnalysisRuns / Analyses
 │         ├── ExtractedFacts
 │         ├── EvidenceSources
 │         ├── Insights
 │         └── Proposed ActionPlans
 ├── Goals
 │    └── GoalMilestones
 ├── ActionPlans
 │    ├── Milestones
 │    └── Tasks
 │         └── TaskDependencies
 ├── Reminders
 └── UserFeedback
```

Relationship rules:

- A user owns each top-level document, analysis context, action plan, task, goal, reminder, and feedback record.
- A document has zero or more processing jobs and extraction pages/results.
- A document can have multiple analysis runs; an analysis run should identify its source document and provider execution state.
- Extracted facts reference evidence through a source location rather than relying only on an unstructured page number.
- Evidence supports insights; an insight can have multiple supporting evidence sources and may record contradictory or missing evidence.
- Insights and verified document requirements may generate proposed action candidates.
- An action plan contains ordered milestones and tasks. A task dependency must reference tasks in an ownership-safe scope and must prevent self-dependencies and cycles at the service layer.
- Goals can relate to multiple action plans and tasks without making either module depend on the other’s implementation details.
- Reminders attach to approved tasks or explicit deadlines and retain timezone and delivery status.
- Feedback can reference an analysis, insight, recommendation, or action proposal and must remain owned by the submitting user.

Cross-module references should use stable IDs and application interfaces rather than importing concrete service implementations in both directions.

## 8. Ownership and authorization rules

- Every user-owned table must carry a direct `user_id` or have a repository-enforced ownership path that can be proven from its parent.
- Every read, update, archive, delete, approve, dismiss, and retry operation must apply ownership filtering before returning or mutating data.
- A child lookup must verify ownership through its parent in the same query/service transaction; accepting a child ID alone is insufficient.
- Role checks remain server-side and reuse the existing `get_current_user` and `require_roles` dependency behavior.
- Admin access must be explicit and auditable; it must not bypass data minimization by default.
- Provider callbacks and background jobs must carry a trusted internal user/entity context and must not accept ownership from untrusted document or AI content.
- AI output cannot grant access, alter ownership, approve plans, or bypass status transitions.
- Persistent memory requires explicit user approval; extracted facts remain document-derived data unless separately approved.
- Logs must exclude passwords, tokens, document contents, evidence quotations where sensitive, and provider secrets.

## 9. Suggested API and service boundaries

### API layer

Keep route handlers thin and versioned under `/api/v1`:

- Documents: upload, list, detail, processing status, analysis request, retry, archive/delete.
- Intelligence: request, result, history, decision support.
- Action plans: propose, list, detail, edit, approve, dismiss, status update.
- Tasks: create/list/update/complete/reopen.
- Goals: create/list/update/milestone progress.
- Reminders: create/list/update/cancel.

No endpoint should directly construct provider calls or contain multi-step business workflows.

### Application services

Proposed service interfaces:

- `DocumentService`
- `DocumentProcessingService`
- `AnalysisService`
- `IntelligenceService`
- `ContextAssemblyService`
- `ActionPlanService`
- `TaskService`
- `GoalService`
- `ReminderService`
- `OwnershipService`

### Repository interfaces

Repositories should expose user-scoped operations, for example:

- `DocumentRepository`
- `AnalysisRepository`
- `EvidenceRepository`
- `InsightRepository`
- `ActionPlanRepository`
- `TaskRepository`
- `GoalRepository`
- `ReminderRepository`
- `FeedbackRepository`

Repository methods should require an ownership context or user ID and should not expose unrestricted generic CRUD to route handlers.

## 10. Migration strategy

1. Install or provision the required tooling in an isolated development environment without changing the application repository.
2. Use the actual runtime configuration, redacting password values, to confirm the target is exactly `orvexa_db` and never `nova_health`.
3. Run read-only `alembic current`, `alembic heads`, `alembic history`, and PostgreSQL catalog queries.
4. Compare `alembic_version` with the migration dependency chain and actual tables.
5. If the state is inconsistent, stop and prepare a reviewed recovery plan; do not stamp, downgrade, or auto-upgrade.
6. Reconcile existing Phase 3 models/migration design before creating new tables.
7. Create only additive, forward-only migrations after schema review.
8. Review generated SQL for drops, implicit destructive changes, missing foreign keys, indexes, ownership columns, and unsafe cascades.
9. Apply only to an isolated development/test database first.
10. Verify the resulting schema and run migration/authentication regression tests.

Existing migrations, particularly `0001_phase2_auth`, must remain unchanged.

## 11. Stage 1B implementation plan

### Can be implemented without database changes

1. Define shared enums and value types for processing status, verification state, confidence, insight kind, proposal status, task status, and priority.
2. Define shared Pydantic schemas for pagination, errors, evidence references, confidence/uncertainty, and ownership context.
3. Define provider interfaces and configuration/health-check contracts.
4. Define service interfaces and repository protocols without wiring new persistence.
5. Define ownership policy interfaces and unit-test authorization decisions.
6. Add pure domain validation for status transitions, task dependency rules, ambiguous dates, and approval requirements.

### Requires verified schema and likely migrations

7. Reconcile existing `Document`, `Analysis`, `ActionPlan`, and `Action` models with live tables.
8. Add only necessary missing ORM models, relationships, indexes, constraints, and timestamps.
9. Add a reviewed forward-only Alembic migration if the verified schema requires changes.
10. Add repositories and application services using user-scoped queries.
11. Add API endpoints only after service/repository contracts are tested.

### Exact safe implementation order

1. Establish an isolated Python environment and install `backend/requirements.txt`.
2. Complete read-only database verification against the intended database.
3. Add shared domain enums/value types.
4. Add shared schemas and validation tests.
5. Add repository/service protocols.
6. Add ownership policy interfaces and tests.
7. Reconcile ORM metadata with verified schema.
8. Prepare and review one additive migration only if required.
9. Implement repository tests and service tests.
10. Run authentication regression, migration, and backend test suites.

Do not start document extraction, AI provider implementation, action execution, Flutter feature work, or Stage 1B database changes until this sequence is approved.

## 12. Testing strategy

### Current foundation regression

- Authentication registration, login, refresh rotation, logout, role enforcement, and ownership behavior.
- Health and readiness behavior.
- Migration revision and seeded role checks against an isolated PostgreSQL database.

### Stage 1B unit tests

- Enum and schema validation.
- Confidence bounds and uncertainty representation.
- Evidence reference validation.
- Ownership decisions for direct and parent-owned records.
- Status transition matrix.
- Task dependency self-reference and cycle prevention.
- Approval requirements for proposed actions.

### Stage 1B integration tests

- Repository queries always scope by user ID.
- Cross-user IDs return not-found or forbidden behavior consistently.
- Existing authentication tables remain compatible.
- Migration SQL contains no destructive operations.
- Schema metadata and live catalog match after an isolated migration.

Tests must use an isolated test database or fixtures. They must never target `nova_health` or an unverified real user database.

## 13. Risks and unresolved questions

- The live database was verified and upgraded, but production-scale data migration and operational backup/restore procedures remain outside this stage.
- The `.env.example` database name differs from the application default and the user-designated database.
- Existing Phase 3 document and analysis relationships remain intentionally minimal; extraction/OCR and provider orchestration are future work.
- Cross-table ownership consistency for parent records is enforced by repositories/services and must remain covered as new write paths are added.

## 14. Verification performed

From an isolated environment with dependencies installed, run from `backend`:

```powershell
python -m alembic history --verbose
python -m alembic heads
python -m alembic current
python -m pytest tests -q
```

Before migration, a read-only PostgreSQL/Alembic session against the confirmed `orvexa_db` inspected:

- `alembic_version`
- `information_schema.tables`
- `information_schema.columns`
- `pg_constraint`
- `pg_indexes`

After the reviewed additive migration, `python -m alembic upgrade head`, `python -m alembic current`, and `python -m alembic check` completed successfully. No downgrade or stamp was run.

## 15. Stage 1B implementation

### Shared foundation

- `backend/app/shared` contains stable string enums for processing, analysis, verification, approval, task, goal, and plan states.
- `utc_now`, timezone-aware timestamp validation, bounded offset pagination (`1..100`), and structured safe error contracts are available for future routes.
- New records use UUID identifiers and timezone-aware PostgreSQL timestamps with database-side UTC defaults where persisted.

### Personal Intelligence and evidence

The new `intelligence_requests`, `analysis_runs`, `intelligence_insights`, `context_references`, and `user_feedback` models are owner-scoped. Confidence and uncertainty remain nullable and are range constrained when supplied. `evidence_sources` supports document or analysis-run references, preserves verification state, and requires at least one validated parent reference at the schema/database boundary.

### Action Engine

The existing `ActionPlan` and `Action` models are reused as the plan and candidate foundation. New `goals`, `goal_milestones`, `tasks`, and `task_dependencies` tables provide the minimal action foundation. Task repositories scope reads by authenticated owner. Services reject cross-user dependencies, self-dependencies, and circular dependencies; task status transitions are explicit and completed tasks cannot transition back to pending.

### Ownership and deletion

Every new user-owned table has a required `user_id` foreign key to `users` with `RESTRICT`. Child records use `CASCADE` only where the child has no independent meaning (task dependencies and goal milestones); user-owned domain records do not cascade from users. Client-supplied user IDs are not used as authorization proof.

### Testing and limitations

The Stage 1B backend suite passed with 17 tests before Stage 2. Stage 2 adds 5 backend tests for signatures, size limits, traversal rejection, hashing, and private storage isolation. The complete backend suite now passes with 22 tests and one pre-existing Starlette/httpx deprecation warning. Stage 2 also adds 5 Flutter tests inherited from the shell; `flutter analyze` reports no issues.

## 16. Stage 2 secure document ingestion

Stage 2 adds `LocalStorageProvider`, bounded document validation, duplicate detection, owner-scoped repository queries, and authenticated document lifecycle routes:

- `POST /api/v1/documents` for multipart upload of PDF, DOCX, TXT, CSV, PNG, JPG/JPEG, and WEBP files.
- `GET /api/v1/documents` and `GET /api/v1/documents/{id}` for owner-scoped metadata.
- `GET /api/v1/documents/{id}/content` for authorized retrieval without exposing physical paths.
- `POST /api/v1/documents/{id}/archive` and `DELETE /api/v1/documents/{id}` for lifecycle operations.
- `POST /api/v1/documents/{id}/retry` for a new queued validation job.

Files are stored outside public directories under a server-generated key. The upload path bounds reads to the configured 25 MiB default, validates extension/media type/signature where applicable, rejects path separators and empty content, hashes content, and never executes uploaded files. Processing is only queued; Stage 3 owns actual extraction.

Migration `0004_document_lifecycle` was reviewed offline and applied to the verified `orvexa_db`. It adds nullable `archived_at` and `deleted_at` columns and `ix_documents_user_archived_at`; it does not modify existing data or authentication tables. The current head is `0004_document_lifecycle`, and `alembic check` is clean.

The Flutter shell now has a real Documents route with file selection, upload progress, list refresh, loading/empty/error states, archive, and deletion confirmation. The current shell has no token/session provider, so authenticated end-to-end UI execution is not claimed until that existing authentication integration is supplied.
