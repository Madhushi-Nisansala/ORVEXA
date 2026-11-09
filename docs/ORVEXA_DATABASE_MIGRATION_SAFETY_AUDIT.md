# ORVEXA Database Migration Safety Audit

**Audit mode:** Read-only. No database connection, SQL state change, migration command, worker start, test execution, credential display, or application-source modification was performed.

**Repository scope:** `backend/` Python/FastAPI/SQLAlchemy/Alembic code, relevant `backend/tests/`, and relevant Flutter API/routing code.

**Evidence convention:** Paths and line numbers refer to the repository source reviewed during this audit. Findings based on the supplied incident record are explicitly identified as supplied facts. Runtime behavior and database state were not inferred from migration source alone.

## 1. Executive Summary

### Confirmed root cause

- **Finding:** The document worker accesses `DocumentProcessingJob.max_attempts` at `backend/app/workers/document_worker.py:48,91`, while the supplied read-only inspection reports Alembic revision `0005_document_extractions` and confirms that `max_attempts` does not exist. Migration `0006_stage2_extraction_jobs` adds that column at `backend/migrations/versions/0006_stage2_extraction_jobs.py:18-21`.
- **Severity:** Critical.
- **Recommended action:** Do not start the worker. After backup and target verification, inspect the actual schema read-only and obtain explicit approval for a narrowly scoped, reviewed migration operation. Do not automatically upgrade to `head`.
- **Database inspection required:** Yes.

### Other critical/high defects

1. `backend/app/modules/extraction/service.py:46-53` creates `DocumentPage` without `extracted_text`, although `backend/app/modules/documents/document_models.py:39` and migration `0002_phase3_documents.py:38` make it non-nullable. Extraction persistence is expected to fail on flush/commit for normal extracted pages.
2. The worker is not automatically started by `backend/app/main.py`; it is independently started through the module entry point in `backend/app/workers/document_worker.py:162-167`. This can leave queued jobs unprocessed unless a separate process manager launches it.
3. `backend/app/modules/intelligence/provider.py:40-59` contains only an unavailable provider and rejects every non-empty provider identifier as unsupported. Document analysis cannot complete with a real provider based on the reviewed source.
4. `backend/app/api/v1/router.py:3-16` does not include `backend/app/api/v1/endpoints/context.py`, so the context routes exist in source but are not registered in the main API router.
5. Task/goal ORM models and services exist, but no task/goal endpoint module or router registration was found. They are not an API capability in the reviewed application.

### Overall migration conclusion

The source migration chain is linear from `0001_phase2_auth` through `0008_stage4_context_privacy`, with one apparent head (`0008_stage4_context_privacy`). Source-level foreign-key dependencies for 0006–0008 are internally ordered correctly. That does **not** establish that the target database contains the prerequisite tables, that it has no partial migration artifacts, or that its data/constraints are compatible. Actual target-schema and backup verification remain outside this audit.

## 2. Confirmed Database State

The following are treated as supplied incident facts and were not independently re-queried:

| Item | Supplied value |
|---|---|
| Database | `orvexa_db` |
| Host/port | `localhost:5432` |
| User | `orvexa` |
| Applied Alembic revision | `0005_document_extractions` |
| `document_processing_jobs.max_attempts` | Does not exist |
| `nova_health` | Not accessed; explicitly excluded from this audit |

- **Finding:** The supplied state is inconsistent with the worker ORM and worker SQL generation, because the ORM maps `max_attempts` and worker queries load/update it.
- **Severity:** Critical.
- **Recommended action:** Treat `orvexa_db` as the only authorized target. Reconfirm target identity using a separately approved, read-only inspection before any migration decision.
- **Database inspection required:** Yes.

- **NOT VERIFIED:** No database connection was made during this audit. The current column set, actual `alembic_version` contents, partial DDL, indexes, constraints, row counts, data quality, locks, active jobs, and backup/recovery status were not independently verified.

## 3. Migration Chain Review

### Revision graph

| Revision | Parent | Source |
|---|---|---|
| `0005_document_extractions` | `0004_document_lifecycle` | `backend/migrations/versions/0005_document_extractions.py:3-14` |
| `0006_stage2_extraction_jobs` | `0005_document_extractions` | `backend/migrations/versions/0006_stage2_extraction_jobs.py:3-14` |
| `0007_stage3_document_analysis` | `0006_stage2_extraction_jobs` | `backend/migrations/versions/0007_stage3_document_analysis.py:3-14` |
| `0008_stage4_context_privacy` | `0007_stage3_document_analysis` | `backend/migrations/versions/0008_stage4_context_privacy.py:3-14` |

Earlier parents are linear from `0001_phase2_auth` through `0004_document_lifecycle`.

- **Finding:** Source metadata shows a single linear head at 0008.
- **Severity:** Low.
- **Recommended action:** Confirm the actual Alembic graph and `alembic_version` table read-only before migration. Source metadata alone is not proof of the target state.
- **Database inspection required:** Yes.

### Common migration safety observations

- All reviewed upgrades use unconditional `create_table`, `add_column`, `create_index`, or constraints. They do not use existence guards. A partially applied migration, manually created object, duplicate index/constraint, or drifted schema can cause the operation to fail.
- `0006` adds non-null columns with constant server defaults, which is generally suitable for existing rows in PostgreSQL, but the operation still requires the table and must be checked against existing column/index names and locks.
- `0007` and `0008` create tables without data backfill. Existing objects with the same names or duplicate unique-key data in a pre-existing table would cause failure.
- `0008` has no usable downgrade: `backend/migrations/versions/0008_stage4_context_privacy.py:73-74` raises `NotImplementedError("ORVEXA migrations are forward-only")`.

- **Finding:** Migration operations are not safely repeatable and the final revision is irreversible through Alembic downgrade.
- **Severity:** High.
- **Recommended action:** Require a schema-drift report, lock/maintenance assessment, backup evidence, and a reviewed recovery plan before applying any migration. Do not use downgrade as a rollback plan for 0008.
- **Database inspection required:** Yes.

## 4. Migration 0006 Compatibility

### Prerequisite tables

- `document_processing_jobs` is created by `backend/migrations/versions/0002_phase3_documents.py:43-50`.
- `document_extractions` is created by `backend/migrations/versions/0005_document_extractions.py:18-34`.
- `document_pages` is created by `backend/migrations/versions/0002_phase3_documents.py:36-42`.

Therefore, the ordered chain gives 0006 the required source dependencies.

### Columns added and ORM comparison

| Table | Migration 0006 | ORM model | Result |
|---|---|---|---|
| `document_processing_jobs` | `max_attempts` integer, non-null, default 3 | `analysis_models.py:17` integer, non-null, Python default 3 | Compatible type/nullability; ORM lacks an explicit server default |
| `document_processing_jobs` | `available_at` timestamptz, non-null, default current timestamp | `analysis_models.py:18` timestamptz, non-null | Compatible type/nullability; ORM has no default |
| `document_processing_jobs` | `claim_token` varchar(64), nullable | `analysis_models.py:20` varchar(64), unique | Compatible; migration creates a unique index |
| `document_processing_jobs` | `claimed_at` timestamptz, nullable | `analysis_models.py:21` timestamptz, nullable | Compatible |
| `document_processing_jobs` | `processing_version` varchar(32), non-null, default `stage2-v1` | `analysis_models.py:24` varchar(32), non-null, Python default | Compatible type/nullability; ORM lacks explicit server default |
| `document_extractions` | `detected_document_type` varchar(32), nullable | `extraction/models.py:25` varchar(32), nullable | Compatible |
| `document_extractions` | `processing_version` varchar(32), non-null, default `stage2-v1` | `extraction/models.py:26` varchar(32), non-null, Python default | Compatible type/nullability; ORM lacks explicit server default |
| `document_extractions` | `language_detection_status` varchar(32), non-null, default `not_run` | `extraction/models.py:27` varchar(32), non-null, Python/server default | Compatible |
| `document_pages` | `extraction_status` varchar(32), non-null, default `completed` | `document_models.py:41` varchar(32), non-null, Python default | Compatible |
| `document_pages` | `ocr_used` boolean, non-null, default false | `document_models.py:42` boolean, non-null, Python default | Compatible |
| `document_pages` | `error_summary` varchar(500), nullable | `document_models.py:43` varchar(500), nullable | Compatible |

- **Finding:** The 0006 columns represented in the ORM match migration names, PostgreSQL-compatible types, lengths, and nullability. The supplied database is nevertheless missing at least `max_attempts`, so the target is behind or drifted relative to the application.
- **Severity:** Critical for the target; Low for source compatibility.
- **Recommended action:** Compare every 0006 column, default, index, and constraint with `information_schema`/`pg_catalog` read-only output for `orvexa_db` before deciding whether 0006 alone is appropriate.
- **Database inspection required:** Yes.

### Index and existing-data risks

- `0006` creates `ix_document_processing_jobs_claimable` on `(status, available_at)` and unique `ix_document_processing_jobs_claim_token` on `claim_token` (`0006:32-42`). A pre-existing object with either name, or a partially applied prior attempt, can fail the upgrade.
- A unique index on nullable `claim_token` is PostgreSQL-compatible: multiple nulls are allowed, while non-null duplicate claim tokens are rejected. Existing non-null duplicates must be checked before creation.
- Adding non-null columns with constant defaults should populate old rows, but existing rows and column/table drift must be verified. No data inspection was performed.

- **Severity:** High.
- **Recommended action:** Read-only-check object names, existing non-null values, duplicate non-null claim tokens, and table locks/size before approval.
- **Database inspection required:** Yes.

## 5. Migration 0007 Compatibility

`backend/migrations/versions/0007_stage3_document_analysis.py:18-40` creates `document_analyses` with:

- UUID primary key `id`.
- UUID foreign keys to `users.id`, `documents.id`, and `document_extractions.id`, all `RESTRICT`.
- Non-null integer `version`.
- Non-null status with PostgreSQL-compatible string default `pending`.
- Nullable provider/model/error fields and nullable JSON `result`.
- Timestamptz creation/completion columns.
- Unique constraint `uq_document_analyses_document_version` and user/document indexes.

### Dependency assessment

- `users` and `documents` exist in source migrations 0001/0002.
- `document_extractions` exists in 0005.
- All referenced columns are primary keys with UUID types in the source migrations.
- ORM `backend/app/modules/intelligence/models.py:26-46` matches the table, foreign keys, unique constraint, indexes, JSON result, and timestamp types.
- `backend/app/modules/intelligence/analysis_service.py:119-148` relies on `(document_id, version)` uniqueness for versioned analysis behavior.

- **Finding:** 0007 is source-order compatible and its ORM mapping is materially aligned with the migration.
- **Severity:** Medium until target verification.
- **Recommended action:** Confirm referenced tables/columns and absence of an existing `document_analyses` table or conflicting constraint. Check existing analysis data for duplicate `(document_id, version)` only if the table already exists outside the migration chain.
- **Database inspection required:** Yes.

- **Finding:** 0007's JSON, UUID, Boolean/timestamp-adjacent definitions are PostgreSQL-compatible as emitted by SQLAlchemy. This is source compatibility only; actual PostgreSQL catalog types were not checked.
- **Severity:** Low.
- **Recommended action:** Verify actual catalog types before any repair.
- **Database inspection required:** Yes.

## 6. Migration 0008 Compatibility

`backend/migrations/versions/0008_stage4_context_privacy.py:18-70` creates `user_context`, `context_preferences`, and `insight_evidence`.

### Foreign-key dependencies

- `user_context.user_id -> users.id` (`0008:37`) exists in 0001.
- `user_context.evidence_reference -> evidence_sources.id` (`0008:38`) exists in 0003 (`0003:107-125`).
- `context_preferences.user_id -> users.id` (`0008:52`) exists in 0001.
- `insight_evidence.user_id -> users.id`, `insight_id -> intelligence_insights.id`, and `evidence_source_id -> evidence_sources.id` (`0008:64-66`) exist in 0001/0003.

### ORM comparison

`backend/app/modules/intelligence/context_models.py:12-86` matches the three table names, UUIDs, string lengths, JSON content, booleans, timestamptz fields, defaults, foreign keys, primary key, unique constraint, and indexes. The migration and ORM use `sa.JSON`/`JSON`, which is PostgreSQL-compatible JSON storage.

- **Finding:** 0008 has valid source-order dependencies and materially compatible ORM mappings.
- **Severity:** Medium until target verification.
- **Recommended action:** Verify all prerequisite tables and referenced columns in the actual target; check object-name collisions and any pre-existing duplicate `(insight_id, evidence_source_id)` pairs if the table already exists.
- **Database inspection required:** Yes.

- **Finding:** `0008` is forward-only and its downgrade raises `NotImplementedError` (`0008:73-74`). Applying it without a tested recovery strategy is irreversible through normal Alembic downgrade.
- **Severity:** High.
- **Recommended action:** Treat backup/recovery evidence and human approval as hard gates. Do not claim or assume a backup exists.
- **Database inspection required:** Yes, plus independent backup verification.

## 7. ORM vs Migration Differences

### Confirmed or material differences

1. **Worker job server defaults:** Migration 0006 defines server defaults for `max_attempts`, `available_at`, and `processing_version` (`0006:18-31`), while `analysis_models.py:17-25` generally supplies Python defaults or no ORM default. Current `DocumentService` explicitly supplies `max_attempts`, `available_at`, `processing_version`, and `created_at` (`document_service.py:56-65,112-115`), so the current enqueue path is covered. Direct SQL inserts or other writers may not be.
   - **Severity:** Medium.
   - **Recommended action:** Inventory all writers and validate whether server defaults are relied upon; add isolated tests before any production change.
   - **Database inspection required:** No for source review; Yes to verify target defaults.

2. **Migration metadata imports:** `backend/migrations/env.py:8-12` imports database models, document models, analysis models, domain models, and extraction models, but does not visibly import `app.modules.intelligence.models` or `context_models`. Explicit migrations do not require those imports, but Alembic autogenerate metadata would be incomplete for those model classes.
   - **Severity:** Medium.
   - **Recommended action:** Review and test autogenerate policy before using it. Never use an unreviewed autogenerate result as a repair.
   - **Database inspection required:** No for source finding; Yes before schema tooling use.

3. **Legacy analysis tables remain:** Migration 0002 creates `analyses`, `extracted_facts`, `action_plans`, and `actions`; 0007 creates the separate `document_analyses` artifact model. This may be intentional versioning, but it creates two analysis representations and should not be treated as interchangeable.
   - **Severity:** Medium.
   - **Recommended action:** Confirm the intended ownership/data flow before applying later migrations or writing compatibility code.
   - **Database inspection required:** Yes to determine actual usage/data.

### PostgreSQL type/default assessment

- UUID mappings use SQLAlchemy `Uuid`/`Uuid()` and source primary/foreign-key columns consistently use UUID.
- JSON mappings use SQLAlchemy JSON and are nullable/non-nullable consistently for reviewed 0005–0008 fields.
- Boolean defaults in 0006/0008 use SQLAlchemy `false()`/`true()` or quoted PostgreSQL-compatible defaults.
- Timestamps use `DateTime(timezone=True)` and `CURRENT_TIMESTAMP`/`func.now()` consistently enough for PostgreSQL timestamptz intent.
- **NOT VERIFIED:** Actual catalog type modifiers, defaults, constraints, indexes, extensions, and existing data were not inspected.

## 8. Worker Failure Root Cause

- **Worker access evidence:** `document_worker.py:39-55` reads/updates `claimed_at`, `attempts`, `max_attempts`, `claim_token`, `available_at`, and `error_message`; `:63-83` queries `status`, `available_at`, `created_at`, then updates attempts/claim fields; `:87-99` reads `max_attempts` and updates retry fields; `:112-129` reads `documents.id/deleted_at` and updates job completion fields.
- **Model evidence:** `analysis_models.py:9-25` maps all those job columns, including `max_attempts`, `available_at`, `claim_token`, `claimed_at`, `processing_version`, and timestamps.
- **Migration evidence:** 0002 supplies the base job columns; 0006 supplies the worker lifecycle columns.
- **Supplied target evidence:** Database is at 0005 and has no `max_attempts`.

**Conclusion:** The immediate crash is expected schema/application drift: the running worker code requires 0006, while the supplied database state has only 0005. Other 0006 columns (`available_at`, `claim_token`, `claimed_at`, `processing_version`) are also absent unless they were added outside Alembic; that is **NOT VERIFIED** and may produce subsequent failures.

- **Severity:** Critical.
- **Recommended action:** Keep worker stopped. Read-only compare all 0006 columns/indexes, then separately repair source defects and obtain approval for the minimum safe database operation.
- **Database inspection required:** Yes.

## 9. Extraction Persistence Bug

- **Schema/model requirement:** `DocumentPage.extracted_text` is non-nullable at `backend/app/modules/documents/document_models.py:39`; migration 0002 defines `document_pages.extracted_text` as `sa.Text(), nullable=False` at `0002_phase3_documents.py:36-41`.
- **Write path:** `backend/app/modules/extraction/service.py:45-53` constructs `DocumentPage` with id, document id, page number, extraction method, extraction status, OCR flag, error summary, confidence, and created time, but does **not** assign `extracted_text=page.text`.
- **Downstream dependency:** `analysis_service.py:110-137` reads `DocumentPage.extracted_text` to build analysis input and `:64-70` validates evidence against it. The document API also returns it (`endpoints/documents.py:127-131`) and searches it (`:61-68`).

**Consequence:** For ordinary extracted pages, the insert/flush/commit should violate the non-null database constraint or otherwise fail before usable page persistence. If a null value were somehow present, downstream analysis and evidence validation could not provide the required text and page persistence would be incomplete. The exact exception timing is **NOT VERIFIED** because no database or worker execution was performed.

- **Severity:** Critical.
- **Recommended action:** Fix and unit/integration-test the source write path separately from migration work. Do not fix it as part of this audit.
- **Database inspection required:** No to confirm the source defect; Yes to determine whether any partial rows were persisted in the target.

## 10. Test Database Safety Classification

No tests were executed.

| Test | Classification | Evidence and safety decision |
|---|---|---|
| `backend/tests/test_phase2_migration.py` | **Configured PostgreSQL; unknown/unsafe target** | `:16-20` uses `get_settings().get_database_url()` and `:24-45` connects and reads `alembic_version`/`roles`. Do not execute until the resolved target is explicitly verified as authorized `localhost:5432/orvexa_db`, and never run it against `nova_health`. |
| `backend/tests/test_documents_api.py` | **Isolated SQLite/in-memory** | `:25-29` creates `sqlite+aiosqlite://` with `StaticPool`; dependency override at `:54-58` routes API DB access to it. Review remains necessary because importing `app.main` constructs the normal engine from settings, although this test's request dependency is overridden. |
| `backend/tests/test_stage3_intelligence.py` | **Isolated SQLite/in-memory** | `:87-90`, `:123-126`, and `:149-151` use SQLite `StaticPool` and `Base.metadata.create_all`; provider tests are controlled/mocked. It does not validate PostgreSQL migrations or worker schema. |
| `backend/tests/test_stage3_extraction.py` | **No database** | Extractor-only tests use in-memory bytes and parser libraries (`:9-40`). They do not test extraction persistence or `DocumentPage` insertion. |
| `backend/tests/test_stage2_documents.py` | **No database** | Validation and local storage use `tmp_path` (`:9-37`); no DB connection is present. |
| `backend/tests/test_stage1b_domain.py` | **No database shown** | The reviewed test targets policy/status logic. No configured database setup was found. |
| `backend/tests/test_auth_security.py` | **Unknown/unsafe until reviewed in detail** | It imports application/auth paths; no classification as an isolated DB was established from the safety scan. Do not run as a suite until its setup and target are explicitly reviewed. |
| `backend/tests/test_health.py` | **Unknown/unsafe for unmodified execution** | `:8` imports the app and `:21-51` monkeypatches connectivity for some tests, but module-level app/session imports can construct the configured PostgreSQL engine. It must not be treated as a database-isolated test without reviewing the full fixture/runtime behavior. |

No dedicated tests were found for worker lifecycle, 0006 schema compatibility, extraction persistence with a non-null `extracted_text`, context/privacy routes, or 0008 migration behavior. Existing SQLite `Base.metadata.create_all` tests do not prove PostgreSQL migration compatibility.

- **Severity:** High.
- **Recommended action:** Add isolated tests for extraction persistence and worker compatibility only after source repair design; add a migration test against a separately provisioned isolated PostgreSQL target, never the configured development database by default.
- **Database inspection required:** Yes before any PostgreSQL-configured test.

## 11. Application Integration Gaps

### Worker startup

- `backend/app/main.py:1-29` creates the FastAPI app and includes routers, but does not start the document worker.
- `backend/app/workers/document_worker.py:146-167` provides a polling loop and module entry point.

**Finding:** The worker is independently launched, not automatically started by the API in reviewed source. **Severity: High.** Recommended action: document and supervise it as a separate process after schema/source verification; do not start it during this audit. Database inspection required: No for source finding.

### Context routes

- `backend/app/api/v1/endpoints/context.py:51-180` defines context and preference routes.
- `backend/app/api/v1/router.py:3-16` imports/includes system, auth, users, admin, documents, and intelligence routers, but not `context.router`.

**Finding:** Context routes are not registered through the main API router based on source. **Severity: High.** Recommended action: register and test separately after approval; no source change was made. Database inspection required: No for source finding.

### Tasks and goals

- `backend/app/modules/actions/models.py:12-76` defines `Task`, `TaskDependency`, `Goal`, and `GoalMilestone`; services/repositories also exist.
- No task/goal endpoint file or router registration was found under `backend/app/api/v1/endpoints` or `router.py`.

**Finding:** Models/services do not have corresponding API endpoints in the reviewed source. **Severity: Medium.** Recommended action: define API scope and migrations/routes separately; do not infer runtime capability from models alone. Database inspection required: Yes to determine whether corresponding tables/data exist in the target.

### AI provider and analysis completion

- `provider.py:40-59` implements `UnavailableProvider` and raises when no provider is configured; any non-empty provider is rejected as unsupported.
- `analysis_service.py:132-148` calls the provider and persists success only after output/evidence validation.
- `intelligence.py:64-75` exposes an analysis endpoint, but no real provider implementation was found.

**Finding:** Analysis endpoints exist in source, but successful runtime analysis cannot be confirmed and appears impossible with the reviewed provider factory. **Severity: Critical for feature availability.** Recommended action: implement/configure a reviewed provider and test its output contract separately. Database inspection required: No for provider source finding; Yes to inspect persisted analysis states.

### Flutter coverage

- `frontend/lib/app/router/app_router.dart:8-30` routes home, documents, document detail, and settings only.
- `frontend/lib/features/documents/data/documents_api.dart:15-67` covers document list/upload/archive/delete/extract/analyze/analysis/retry/pages.
- No Flutter context, task, or goal API client/feature was found in the reviewed `frontend/lib` inventory.

**Finding:** Flutter covers a subset of document and analysis endpoints but not context, task, or goal capabilities. Runtime compatibility with the backend was not verified. **Severity: Medium.** Recommended action: align API contracts and add client coverage after backend routes are actually registered. Database inspection required: No for source finding.

## 12. Risks and Severity

| Risk | Severity | Database inspection required |
|---|---|---|
| Worker requires missing `max_attempts` and likely other 0006 columns | Critical | Yes |
| Extraction service omits required `DocumentPage.extracted_text` | Critical | Yes for persisted-impact assessment; source defect is confirmed without DB |
| Applying 0006 to a drifted/partial schema can fail on missing tables or duplicate objects | High | Yes |
| 0008 has no Alembic downgrade | High | Yes, plus verified recovery/backup evidence |
| PostgreSQL-configured migration test can connect to an unintended target | Critical | Yes before execution; do not execute now |
| No verified backup evidence | Critical gate | Yes/independent backup evidence |
| Context source routes are not registered | High | No for source finding |
| No real analysis provider implementation | Critical feature risk | No for source finding |
| Worker not API-started | High | No for source finding |
| No task/goal API endpoints | Medium | Yes for actual target data/table status |
| ORM/server-default differences and incomplete Alembic metadata imports | Medium | Yes before schema tooling/use |
| Actual target state, locks, data duplicates, and constraints | Critical unknown | Yes |

## 13. Recommended Repair Sequence

1. **Verify a recoverable backup exists** through reliable operational evidence. If it cannot be verified, stop; do not claim one exists.
2. **Confirm the exact authorized target** is `localhost:5432/orvexa_db`, including database identity, without accessing `nova_health` and without displaying credentials.
3. **Inspect current schema and migration state read-only**, including `alembic_version`, tables, columns, defaults, indexes, constraints, foreign keys, locks, and relevant row/duplicate checks.
4. **Compare the actual target specifically with 0006**, including all five job columns, three extraction columns, three page columns, and both indexes. Determine whether the state is cleanly at 0005 or partially drifted.
5. **Review 0007 and 0008 against the actual target**, including referenced tables, object-name collisions, unique-key conflicts, and readiness of application code. Do not assume upgrading to `head` is correct.
6. **Fix source defects separately**, especially the missing `extracted_text` assignment, and separately resolve route/provider/integration gaps. Do not bundle source repairs implicitly into a database migration.
7. **Add isolated tests** for extraction persistence, worker model/schema compatibility, and provider/analysis behavior. Add a migration test only against a disposable, explicitly isolated PostgreSQL database.
8. **Obtain explicit human approval** that names the target, revision(s), backup/recovery evidence, maintenance window, and rollback/recovery plan.
9. **Apply only the approved migration operation**, using the reviewed target and no automatic unreviewed upgrade to head.
10. **Verify the resulting schema read-only**, including columns/defaults/indexes/constraints and Alembic revision.
11. **Start the worker only after schema and source verification**, with monitored logs and a controlled test job.

## 14. Pre-Migration Checklist

- [ ] `nova_health` has not been accessed and is excluded from all commands/configuration.
- [ ] Target identity independently confirmed as `localhost:5432/orvexa_db`.
- [ ] Credentials remain hidden; `.env` is not modified or displayed.
- [ ] Recoverable backup exists and restoration/recovery evidence is verified.
- [ ] Current Alembic revision read-only verified.
- [ ] Actual tables/columns/defaults/indexes/constraints/FKs read-only captured.
- [ ] 0006 prerequisites and all existing data compatibility checks completed.
- [ ] Duplicate/non-null claim tokens checked before the unique index.
- [ ] 0007/0008 readiness and object collisions checked.
- [ ] Source defect involving `extracted_text` repaired and tested separately, if approved.
- [ ] Worker remains stopped until after verification.
- [ ] PostgreSQL-targeted tests are not run against the configured application database.
- [ ] Human approval explicitly identifies the exact migration action; no automatic `upgrade head` assumption.
- [ ] Post-operation read-only verification plan is prepared.

## 15. Explicitly Unverified Items

The following were not verified and must not be represented as facts:

- Actual live schema beyond the supplied `max_attempts` absence and supplied revision.
- Whether `available_at`, `claim_token`, `claimed_at`, `processing_version`, or other 0006 columns are also missing.
- Actual Alembic heads or `alembic_version` contents beyond the supplied `0005_document_extractions` fact.
- Whether any migration was partially applied, manually edited, or applied outside Alembic.
- Existing rows, nulls, duplicates, orphaned foreign keys, duplicate indexes/constraints, locks, table sizes, or migration duration.
- Whether a recoverable backup exists or has been successfully restored/tested.
- Runtime behavior of the worker, API, migrations, tests, provider, or Flutter client.
- Whether the configured `.env` resolves to the supplied target; source defaults and configuration wiring were reviewed without reading/displaying `.env`.
- Whether any process manager, container, scheduler, or deployment script starts the worker outside the reviewed Python source.
- Whether context routes are mounted elsewhere outside the reviewed main router.
- Whether task/goal endpoints exist outside the reviewed backend endpoint inventory.
- Whether a real AI provider exists in an external package or deployment not present in the repository.
- Whether the target contains data in legacy `analyses` or newer `document_analyses` tables.
- Whether PostgreSQL-specific behavior differs from the SQLite-based tests.

## Final concise summary

- **Confirmed root cause:** The worker requires 0006's `document_processing_jobs.max_attempts`, but the supplied target is at 0005 and lacks that column.
- **Other critical defects:** Extraction persistence omits required `DocumentPage.extracted_text`; no reviewed real AI provider can complete analysis; context routes are not registered; the worker is independently launched and not started by the API.
- **Migration risks:** Actual schema drift/partial application, duplicate objects/data conflicts, unverified backup state, and irreversible 0008 downgrade behavior. Source compatibility is not evidence of live-schema safety.
- **Recommended next actions:** Keep the worker stopped; verify backup and target; perform read-only schema comparison; repair/test source defects separately; obtain explicit human approval for only a reviewed migration operation; verify schema read-only before worker startup.
