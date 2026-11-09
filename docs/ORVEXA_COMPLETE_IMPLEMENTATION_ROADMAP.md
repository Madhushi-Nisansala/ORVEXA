# ORVEXA Complete Implementation Roadmap

**Product:** ORVEXA — Understand More. Act Smarter.

**Audit scope:** Read-only repository inspection of the backend, Flutter frontend, migrations, tests, configuration templates, deployment files, and existing documentation.

**Audit status:** Complete at source level. Runtime database state, live PostgreSQL behavior, external AI providers, workers, and deployment were not executed.

**Safety statement:** No `.env` secret contents were read. No database connection, migration, worker start, destructive database/Git operation, or deployment was performed. The prohibited `nova_health` database was not accessed.

## 1. Executive summary

ORVEXA is a modular-monolith foundation with a FastAPI backend, Flutter client, PostgreSQL/SQLAlchemy/Alembic persistence, secure token storage, document upload and extraction code, structured document analysis code, evidence models, user context APIs, and task/goal domain code. The current Flutter application provides authentication, dashboard, service status, documents, document details, upload, and limited extraction/analysis presentation.

The repository is not yet a production-ready Personal Intelligence & Action Platform. The most important work is to make the existing document and analysis pipeline truthful and operationally safe before adding higher-level decision and action features. The implementation must proceed in small stages, with focused tests and an approval gate after every stage.

The recommended architecture remains a provider-independent modular monolith. New capabilities should be introduced behind application services and typed API contracts rather than by adding microservices prematurely.

## 2. Current repository status

### 2.1 Implemented or substantially implemented at source level

- FastAPI application with versioned `/api/v1` routing and OpenAPI documentation.
- User registration, login, current-user retrieval, access tokens, refresh-token rotation/revocation code, password hashing with Argon2, and authenticated route dependencies.
- Dashboard, authentication, settings, backend status, documents, and document-detail Flutter routes.
- Dio-based API client with access-token provider and Flutter secure token storage.
- Document upload endpoint, ownership filtering, list/search/detail/content/archive/delete operations, duplicate hash detection, generated storage keys, local private storage, size/type validation, and pagination parameters.
- Document lifecycle fields including queued/processing/completed/failed-related states, extraction records, document pages, processing jobs, attempts, claim tokens, stale-job recovery, and retry/backoff code.
- PDF, DOCX, TXT, CSV, and image/OCR extraction support in source code, subject to runtime capability and provider configuration.
- Structured analysis schemas, versioned analysis records, provider abstraction, OpenAI adapter, output validation, evidence-reference validation, and prompt-injection defensive instructions.
- Evidence-source, insight, user-context, context-preference, feedback-related, task, goal, milestone, dependency, and action-domain source models/services.
- Authenticated API tests using isolated SQLite fixtures and focused Flutter tests for authentication, dashboard, status, documents, navigation, and API behavior.
- Worker startup guards that reject unapproved database targets, including `nova_health`, and require an independently verified schema revision.

### 2.2 Partially implemented or not proven at runtime

- The backend document API is more complete than the Flutter UI: upload is currently single-file, reads the whole file into memory, and has limited progress/error/cancellation handling.
- Extraction persistence and worker behavior are covered by source/tests but have not been verified against the configured PostgreSQL target in this audit.
- The worker is a separately launched process and is intentionally not started by the API. Queued processing therefore requires an explicitly managed worker deployment.
- External AI processing is intentionally blocked in the analysis service until an explicit consent design exists. OpenAI configuration is backend-only, but provider health, usage/cost tracking, and alternative providers are not complete.
- Context and action APIs exist, but the Flutter client does not expose the requested context, memory, decision, action approval, tasks, goals, milestones, or feedback workflows.
- The dashboard still labels intelligence and tasks/goals as coming soon.
- Existing documentation and README status statements are stale relative to current source and must be reconciled without declaring unverified functionality complete.

### 2.3 Missing or materially incomplete

- Complete Stage 10 upload experience: multi-file policy, robust validation feedback, cancel/retry UX, duplicate resolution UX, processing-status screen, and detail refresh behavior.
- Fully verified and idempotent extraction pipeline with real OCR provider configuration, safe job lifecycle semantics, empty/corrupt/unsupported handling, and operational runbook.
- Consent-aware real AI integration with provider factory, normalized errors, rate limits, token/cost accounting, provider health, structured retries, and explicit opt-in integration tests.
- Complete analysis/insight/evidence UX and persistence for source-grounded facts, risks, obligations, recommendations, uncertainty, conflicts, corrections, and feedback.
- Consequential action proposal and explicit approval workflow with history and auditability.
- Complete task, goal, milestone, progress, activity timeline, reminder, notification, and timezone-aware scheduling experience.
- User preferences/context controls and a separate user-approved persistent memory lifecycle. Existing context is not by itself a complete memory system.
- Decision workspace, inspectable criteria/priorities/scoring methodology, alternatives, trade-offs, unknowns, and final user decision capture.
- Broad security hardening: API-wide rate limiting, security headers, audit events, retention/export/deletion controls, dependency scanning, observability, and production backup/recovery verification.
- Release configuration and deployment verification.

## 3. Architecture direction

Use a modular monolith with these boundaries:

- **Presentation:** Flutter screens, Riverpod providers, typed client models, route guards, loading/error/empty/success states.
- **API:** FastAPI routers under `/api/v1`, typed Pydantic request/response schemas, consistent error envelopes, OpenAPI contracts.
- **Application services:** orchestration for documents, extraction, analysis, evidence, actions, tasks, goals, context, memory, decisions, notifications, and feedback.
- **Domain:** lifecycle/state-transition rules, approval boundaries, evidence semantics, ownership rules, uncertainty classification, and retention policies.
- **Data access:** SQLAlchemy repositories and transaction boundaries; all queries scoped to authenticated user ownership.
- **External providers:** interfaces and adapters for AI, OCR, file storage, notifications, job execution, and optional embeddings/vector search.

Do not add microservices unless load, isolation, or provider-operational requirements are documented and demonstrated. Workers remain separate processes operationally, but use the same application/domain contracts.

## 4. Proposed stage order and dependencies

The requested stages are retained, but implementation order is dependency-aware:

1. **Stage 10 — Upload UI and upload flow** depends on the existing auth/client/document contracts and establishes the user-visible document lifecycle.
2. **Stage 11 — Processing and extraction** depends on Stage 10 identifiers/statuses and must be verified before analysis is promoted.
3. **Stage 12 — Real AI provider integration** depends on stable extracted page contracts, consent, provider configuration, and failure semantics.
4. **Stage 13 — Analysis and insights** depends on Stage 11 extraction and Stage 12 provider contracts.
5. **Stage 14 — Evidence, risks, recommendations** depends on validated analysis evidence and source references.
6. **Stage 15 — Tasks, goals, and actions** depends on approved recommendations and explicit action policy.
7. **Stage 16 — Progress and notifications** depends on task/goal/action state transitions and user preferences/timezone.
8. **User context, preferences, and approved memory** should be integrated across Stages 12–16, with persistent memory approval completed before it can affect personalization.
9. **Advanced decision support and feedback personalization** depend on evidence, context controls, action boundaries, and auditable feedback semantics.
10. **Stage 17 — Security, errors, and end-to-end testing** hardens all preceding capabilities and verifies the core workflow.
11. **Performance, privacy, and production reliability** is applied incrementally, with final verification in Stage 17.
12. **Stage 18 — Deployment and MVP release** starts only after acceptance criteria and production-readiness checks pass.

Each stage ends with focused tests, analyzer/static checks, backward-compatibility review, a truthful completion report, and an explicit pause for approval.

## 5. Stage roadmap

### Stage 10 — Document upload UI and upload flow

**Objective:** Give users a reliable Windows-desktop-first upload workflow without replacing existing document behavior.

**Backend work:**

- Preserve and verify the existing `POST /api/v1/documents` contract.
- Return typed validation and duplicate responses suitable for field-level UI messages.
- Confirm allowed formats and content-signature validation for PDF, TXT, DOCX, PNG, JPG/JPEG, and any format retained by the extractor.
- Add/verify upload idempotency or a documented duplicate policy.
- Add document status/detail response fields needed for polling and refresh.
- Keep generated storage identifiers private and files outside static/public directories.

**Frontend work:**

- Add a dedicated upload screen and route using the existing `DocumentsApi`, `ApiClient`, secure token store, and Riverpod conventions.
- Support file picker, Windows drag-and-drop only if the selected package/platform supports it safely, file name/size/type validation, progress, retry, cancellation where supported, duplicate handling, and truthful success only after backend confirmation.
- Add a document processing status/detail experience and refresh the list after confirmed upload.
- Preserve existing list, empty, loading, error, retry, back navigation, archive, delete, and detail behavior.

**Database impact:** Likely none if existing document/job fields are sufficient; any idempotency or upload-session schema requires a migration proposal and approval. Do not run a migration.

**Acceptance criteria:** Authenticated owner can upload supported files, invalid files are rejected server-side, another user cannot access them, duplicate behavior is understandable, progress/errors are truthful, and focused backend/Flutter tests pass.

**Complexity:** Medium.

### Stage 11 — Document processing and text extraction

**Objective:** Make extraction dependable, idempotent, page-ordered, recoverable, and operationally explicit.

**Backend work:**

- Verify the `DocumentPage.extracted_text` persistence path, including empty text and failed-page records.
- Verify transaction behavior so failed extraction does not leave duplicate pages or corrupt prior successful versions.
- Add/verify extraction versioning, page uniqueness, status transitions, processing timestamps, retry limits, exponential backoff, claim-token ownership, stale lease recovery, and safe job finalization.
- Keep the worker separate; document its safe startup checks and never auto-start it.
- Configure a real OCR adapter interface and capability reporting. OCR failures must be explicit, never fabricated.
- Add safe handling for corrupted, empty, unsupported, oversized, and malformed content.

**Database impact:** May require constraints/indexes or extraction-attempt history. Before any migration, inspect migration history and read-only target identity; confirm exactly `orvexa_db` on `localhost:5432` with user `orvexa`; obtain explicit approval; back up and define recovery. No migration in this audit.

**Acceptance criteria:** Repeated processing is idempotent, page text is stored in the intended field, failed jobs retry and eventually fail visibly, stale jobs recover, unsupported/OCR-unavailable cases are truthful, and isolated tests cover all states.

**Complexity:** High.

### Stage 12 — Real AI provider integration

**Objective:** Provide a replaceable, consent-aware, backend-only AI integration without fake results.

**Backend work:**

- Keep `DocumentIntelligenceProvider` as the contract and add a provider factory with configuration validation.
- Add explicit user/tenant consent and external-processing policy before transmitting private document content.
- Normalize timeout, authentication, rate-limit, quota, transient, malformed-output, and unavailable-provider errors.
- Add bounded retries, request timeouts, structured logging without secrets, provider health reporting, and optional token/cost usage persistence.
- Support a primary provider and replaceable alternative through configuration, not business-logic provider names.
- Keep real-provider tests opt-in and credential-gated; ordinary tests use mocked providers.

**Database impact:** Provider configuration is environment/secret-manager data. Usage/cost, consent, and provider-run audit records likely require a migration proposal and approval.

**Acceptance criteria:** No credentials reach Flutter, no provider credentials means a usable but clearly unavailable AI state, consent is required before external processing, valid provider output is schema-validated, and failures never become fake analysis.

**Complexity:** High.

### Stage 13 — Document analysis and insights

**Objective:** Turn extracted text into versioned, structured, source-linked intelligence.

**Backend work:**

- Preserve analysis version history and add/verify schemas for document type, summary, facts, entities, dates, deadlines, amounts, obligations, responsibilities, requirements, opportunities, risks, clarification questions, and suggested next steps.
- Store provider/model/run metadata, timestamps, coverage, errors, and structured result status.
- Ensure every item identifies source fact, source claim, inference, assumption, unknown, or conflict.
- Provide document/analysis insight endpoints with pagination and version selection.
- Add correction and usefulness feedback contracts without silently changing important preferences from one event.

**Frontend work:**

- Add analysis status, summary, insight categories, source page/text references, version display, refresh, unavailable/error, partial, conflict, and correction states.
- Never present an inference as a verified fact.

**Database impact:** Existing analysis/insight structures may need additional normalized insight/version/feedback fields; propose and approve migrations before execution.

**Acceptance criteria:** Analysis is unavailable or partial when appropriate, versions are not overwritten, evidence references validate against extracted pages, and UI labels uncertainty clearly.

**Complexity:** High.

### Stage 14 — Evidence, risks, and recommendations

**Objective:** Provide evidence-grounded decision support with visible uncertainty.

**Backend work:**

- Complete links among user, document, page, extraction, insight, recommendation, risk, and proposed action.
- Validate page/section/excerpt references and detect conflicting source claims.
- Store recommendation rationale, alternatives, missing information, potential consequences, uncertainty, and professional-review notices where applicable.
- Add challenge/correction workflows and prevent unsupported legal, medical, or financial conclusions.

**Frontend work:**

- Add Insights, Evidence, Risks, and Recommendations screens with source navigation, confidence/uncertainty explanation, conflict states, challenge/correction controls, and alternative options.

**Database impact:** Existing evidence sources are a foundation; recommendation/risk/challenge/audit entities likely require approved migrations.

**Acceptance criteria:** Every important recommendation has inspectable evidence or an explicit missing-evidence state; unsupported conclusions are not presented as facts.

**Complexity:** High.

### Stage 15 — Tasks, goals, and action management

**Objective:** Convert approved insights into user-controlled work.

**Backend work:**

- Verify and complete task CRUD, status transitions, priorities, due dates, notes, document/insight links, history, dependencies, goals, milestones, and progress calculations.
- Implement action proposals with statuses Proposed, Approved, Rejected, In Progress, Completed, Cancelled, and Failed.
- Require explicit user approval for every consequential action and record approval/rejection history, actor, timestamp, reason, and source.
- Never send email, submit forms, pay, sign, contact third parties, accept contracts, or create obligations automatically.

**Frontend work:**

- Add Tasks, Goals, Milestones, and action-review screens with confirmation dialogs, status editing, due dates, links to evidence, and truthful unavailable states.

**Database impact:** Existing task/goal/milestone tables are a foundation; action proposals, history, insight links, and audit events may require approved migrations.

**Acceptance criteria:** Users can manage work, AI suggestions remain proposals, consequential actions cannot bypass approval, and ownership isolation is tested.

**Complexity:** High.

### Stage 16 — Progress tracking and notifications

**Objective:** Help users track approved work without claiming undelivered notifications.

**Backend work:**

- Add dashboard summaries, upcoming/overdue calculations, activity timeline, notification preferences/history/read state, reminder scheduling/cancellation, deduplication, and timezone-aware scheduling.
- Define provider interfaces for email/push/in-app notifications and record provider-confirmed delivery status only.
- Keep workers separate and document their dependencies and startup procedure.

**Frontend work:**

- Add progress dashboard panels, activity timeline, Notifications, and notification settings screens.
- Respect disabled preferences and show pending/failed delivery states honestly.

**Database impact:** Notification, schedule, delivery-attempt, preference, and activity tables likely require approved migrations.

**Acceptance criteria:** Disabled reminders are not scheduled, duplicate reminders are prevented, timezones are respected, and delivery is not claimed without provider confirmation.

**Complexity:** High.

### User context, preferences, and user-approved memory

**Objective:** Make personalization transparent, scoped, and user-controlled.

**Current state:** User context and preference models/routes exist with confirmation/rejection and retention fields. The Flutter UI and a distinct persistent-memory lifecycle are missing.

**Implementation:**

- Add User Context and Preferences screens for viewing, editing, category permission, deletion, and disabling use.
- Separate temporary interaction context from persistent memory.
- Implement memory candidates with explanation, source references, approval/edit/reject, category, timestamps, last-used, retention, revoke, and deletion states.
- Ensure only approved active memories are retrievable; rejected/deleted memories cannot be used.
- Do not infer sensitive characteristics or silently convert documents into memory.

**Database impact:** Existing context tables may support part of this; candidate/approval/history/use-record tables likely require approved migrations.

**Acceptance criteria:** A user can inspect and revoke personalization, and tests prove deleted/rejected/unapproved memory is excluded.

**Complexity:** High.

### Advanced decision support

**Objective:** Help users compare choices without making decisions for them.

**Implementation:**

- Add decision workspace, statement, options, user-defined criteria/priorities, benefits, risks, supported costs, time/dependencies, unknowns, trade-offs, scenarios, alternatives, and rationale.
- Do not invent numerical scores or probabilities. If scoring is later introduced, document the methodology and expose all inputs.
- Require the user to record the final decision separately from AI recommendations.

**Database impact:** Decision, option, criterion, evidence-link, scenario, and decision-history tables likely require approved migrations.

**Acceptance criteria:** Users can change criteria/priorities, inspect uncertainty and alternatives, and retain final decision ownership.

**Complexity:** High.

### Feedback-based personalization

**Objective:** Use explicit feedback within documented, reversible boundaries.

**Implementation:**

- Support usefulness/correction feedback for summaries, insights, recommendations, risks, tasks, and notifications.
- Store feedback reason and scope; expose correction/rejection controls.
- Do not claim model retraining. Do not alter important preferences from a single feedback event.
- Allow personalization disablement and transparent change history.

**Database impact:** Existing UserFeedback-related source types need endpoint/UI/retention completion; additional audit/history fields may require approval.

**Complexity:** Medium.

### Stage 17 — Security, error handling, and end-to-end testing

**Objective:** Verify the complete workflow and harden all trust boundaries.

**Security review:**

- Authentication, expiry, refresh rotation, secure Flutter storage, password handling, authorization, user isolation, and RBAC.
- Upload size/signature/MIME/path traversal/filename/storage/execution controls.
- SQLAlchemy parameterization, input validation, CORS allow-list, security headers, API-wide rate limits, and safe error envelopes.
- Prompt injection and untrusted document/external-content handling; no SSRF unless separately designed and constrained.
- Worker claim isolation, retries, retention, audit events, backup/recovery, dependency vulnerability checks, and sensitive-log review.

**Testing:**

- Keep tests on SQLite or isolated test PostgreSQL fixtures; never use production `orvexa_db` for tests.
- Add focused backend and Flutter tests for auth, upload, extraction, provider failures, analysis/evidence, tasks/goals, approval boundaries, memory, notifications, isolation, retries, and recovery.
- Add an isolated end-to-end test for REGISTER → LOGIN → UPLOAD → EXTRACT → ANALYZE → INSIGHTS → EVIDENCE → APPROVE ACTION → TASK → PROGRESS.
- Report exact commands and actual results. Real-provider tests must be explicit and never run in the ordinary suite.

**Database impact:** Security/audit/retention/export/deletion/index changes require separate reviewed migrations. No migration is implied by this roadmap.

**Complexity:** Very high.

### Performance, privacy, and production reliability

Implement incrementally and measure rather than inventing claims:

- Pagination, query/index review, bounded concurrency, background processing, timeouts, retry/idempotency controls, safe caching, structured logs, metrics, tracing/error reporting, health/readiness checks, resource limits, file retention, user data export/deletion, and configuration validation.
- Ensure private data is never cached across users and AI calls are minimized.
- Add backup/recovery runbooks and verify them in an isolated environment before release.

**Complexity:** High.

### Stage 18 — Deployment and MVP release

**Objective:** Prepare, document, and verify an MVP release without deploying automatically.

**Deliverables:**

- Backend/container configuration, Flutter release configuration, HTTPS/domain guidance, secure environment/secret-manager configuration, private file storage, AI/OCR/notification provider configuration, and separate worker deployment instructions.
- Reviewed database migration procedure with backup, target verification, approval, validation, and rollback/recovery plan. Alembic downgrade is not assumed to be a rollback mechanism.
- Monitoring/logging/health checks, release versioning, rollback, onboarding, privacy policy requirements, and terms/conditions requirements.
- MVP release checklist and production-readiness checklist with evidence for every claimed item.

**Database impact:** Production migration execution is explicitly outside this audit and requires separate user approval after read-only target verification.

**Complexity:** High.

## 6. Proposed database design evolution

The existing schema should be extended only when a capability cannot be represented safely by current tables. Candidate additions, in dependency order, are:

1. Upload idempotency/session records if needed by Stage 10.
2. Extraction attempt/version/page uniqueness and OCR-provider metadata if needed by Stage 11.
3. External-processing consent, provider run usage/cost, and provider audit records for Stage 12.
4. Normalized insight/recommendation/risk/challenge/feedback records for Stages 13–14.
5. Action proposal and approval history records for Stage 15.
6. Activity, reminder, notification preference/history/delivery records for Stage 16.
7. Memory candidate/approval/use/history records for controlled memory.
8. Decision workspace records and transparent decision history.
9. Security audit, retention, export, deletion, and operational records for Stage 17/18.

Before every migration: inspect the full Alembic chain and target state read-only; verify the target is exactly `orvexa_db` at `localhost:5432` for user `orvexa`; establish backup/recovery; explain the SQL/schema changes; obtain explicit approval; then execute only the reviewed migration and verify it. Never connect to or modify `nova_health`. Never automatically migrate to `head`.

The root `.env.example` and Compose defaults currently use `orvexa` in places, while application defaults and the safety requirements specify `orvexa_db`. This configuration inconsistency is a release blocker and must be resolved through a reviewed, non-secret configuration change before runtime or migration operations. It must not be resolved by guessing at a live database target.

## 7. API design principles

- Keep all product APIs under `/api/v1`.
- Use typed Pydantic schemas and consistent error envelopes with trace identifiers that do not contain secrets.
- Scope every resource query and mutation to the authenticated user or an explicit authorized role.
- Use explicit status-transition endpoints or service rules for documents, jobs, actions, tasks, goals, notifications, memories, and decisions.
- Make pagination bounded and stable.
- Return source references and uncertainty in analysis/evidence responses.
- Return provider unavailable/consent required/partial/failed states instead of fabricated content.
- Generate OpenAPI documentation from actual registered routes and reconcile route documentation with implementation.

## 8. Flutter product design

Preserve the current visual identity and existing routes while adding real functionality only. The target screen set is:

1. Login and registration.
2. Dashboard.
3. Documents, upload, document details, and processing status.
4. Analysis, insights, evidence, risks, and recommendations.
5. Decision workspace.
6. Tasks, goals, milestones, and activity timeline.
7. Notifications and notification settings.
8. User context, preferences, memory management, feedback, and settings.
9. Backend/service status.

Every interactive control must call a real API/action or be visibly marked unavailable. All screens require loading, empty, retryable error, partial/unavailable, confirmation, and success states appropriate to the operation. Windows desktop is the first target; platform-specific support must be capability-checked rather than implied.

## 9. External services and credentials

Potential external dependencies are:

- PostgreSQL at the authorized local target only; isolated SQLite/test PostgreSQL for tests.
- OCR provider or locally configured OCR executable, with language and timeout configuration.
- Primary and alternative AI providers, configured only on the backend through a secret manager/environment.
- Private object/file storage provider for production.
- Email/push notification provider if external notifications are enabled.
- Optional queue/scheduler and monitoring/error-reporting services.

No credentials are present in this roadmap. Provider integrations must remain disabled or clearly unavailable until configured and explicitly consented where private document content is transmitted.

## 10. Risks and blockers

### Critical blockers

- Live database target/schema/version is not verified in this audit. Migration or worker execution is prohibited until read-only target confirmation and user approval.
- Root Compose/template defaults conflict with the required database name `orvexa_db`; this must be resolved before runtime deployment work.
- Worker operation depends on a separately managed process and independently verified schema revision; it must not be started automatically.
- External AI processing is intentionally blocked pending consent and privacy design.
- Existing documentation contains stale status claims and must be updated only with evidence.

### Material risks

- In-memory upload bytes can create client memory pressure for larger files.
- Local storage is not a production durability/retention solution.
- In-memory auth rate limiting is not suitable for multiple backend instances.
- Analysis and document APIs may need expanded pagination, history, and feedback contracts.
- Notification delivery, deletion/export, auditability, and backup recovery are not yet demonstrated.
- Platform differences in Flutter file picker/drag-and-drop and secure storage require platform tests.

## 11. Production-readiness acceptance criteria

ORVEXA must not be called production-ready until all of the following have evidence:

- Core workflow passes in isolated end-to-end tests with actual status transitions.
- Cross-user isolation and approval boundaries pass negative tests.
- No fabricated extraction, AI, evidence, notification, or action results occur.
- Provider outages, OCR failures, worker retries, stale claims, and malformed outputs are recoverable and visible.
- Secrets are externalized; logs contain no credentials, tokens, authorization headers, or unnecessary private content.
- Database target, schema, backup, recovery, migration, and rollback/recovery procedures are documented and tested in a safe environment.
- Pagination, limits, timeouts, rate limits, resource bounds, monitoring, health checks, retention, export, and deletion are verified.
- Flutter analyzer, backend static checks, focused tests, isolated integration tests, and release builds pass with exact results recorded.
- Privacy policy, terms, consent, external-processing disclosures, and user controls are ready for the intended MVP scope.

## 12. Immediate next step

After the user approves this roadmap, begin **Stage 10 — Document upload UI and upload flow** only. Before editing Stage 10, inspect the exact current upload-related files again, preserve existing changes, define the minimal API/UI contract, and state whether a migration is required. Do not run migrations, start workers, connect to a database, deploy, or access `.env` secrets as part of Stage 10 implementation.

Until approval, the completion status of this roadmap is **IMPLEMENTED — NOT VALIDATED**: the document itself has been created from a read-only audit, but the product stages described here have not been implemented or validated by this audit.
