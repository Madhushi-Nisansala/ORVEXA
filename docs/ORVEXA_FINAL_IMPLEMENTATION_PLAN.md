# ORVEXA Final Implementation Plan

**Plan status:** Source-audited plan; implementation and runtime validation are staged.

## Safety constraints

- Never access, modify, migrate, reset, truncate, delete, or inspect `nova_health`.
- Do not run migrations against any configured PostgreSQL database without explicit approval after presenting target identity, current revision, target revision, schema changes, backup/recovery plan, and exact command.
- Do not start the real document worker until the approved target and required schema revision are independently verified.
- Do not send documents to external AI providers, consume paid credits, send notifications, deploy, or delete user data without explicit approval.
- Preserve untracked and user-modified files. Avoid destructive Git operations.
- Use isolated SQLite or explicitly isolated test PostgreSQL resources for automated tests.

## Implementation principles

1. Verify current source before each stage; do not infer completion from models or placeholders.
2. Keep the modular monolith architecture and existing authentication/API client patterns.
3. Make the smallest coherent change and update matching tests and documentation.
4. Keep backend validation authoritative; keep client validation informative and accessible.
5. Never fake progress, provider results, delivery confirmation, or test output.
6. Record each stage as `COMPLETE — VERIFIED`, `IMPLEMENTED — NOT VALIDATED`, `PARTIALLY IMPLEMENTED`, `BLOCKED`, or `NOT IMPLEMENTED`.

## Stage sequence

### Stage A — Configuration and safety baseline

**Scope:** Establish the documented database contract without silently changing an active target; add redacted configuration diagnostics and test safeguards.

**Acceptance criteria:**

- Source templates consistently document the intended ORVEXA development database contract.
- Active `.env` values are not printed or changed by the implementation.
- Worker guard continues to reject `nova_health`, unapproved hosts/ports, and unverified schema revisions.
- Migration chain 0001–0008 is documented as forward-only where applicable.

**Validation:** static configuration tests and redacted source review. Live target verification and migration remain approval-gated.

### Stage B — Stage 10 document upload

**Scope:** Complete Flutter upload UX and reduce unnecessary whole-file buffering in the backend.

**Acceptance criteria:**

- Supported formats and maximum size are displayed from an authoritative capability contract.
- Client validates extension, empty files, and size before upload; backend remains authoritative.
- Multiple selection is used where the platform supports it.
- File name and size are visible; each upload has real Dio progress, retry, and cancellation where supported.
- Duplicate, unauthorized, expired-token, server, and network failures have clear messages.
- Successful uploads refresh the list and expose processing status/detail navigation.
- Backend uses bounded-memory temporary storage/streaming or equivalent safe bounded handling, validates content, atomically stores files, and cleans temporary files.

**Tests:** focused Flutter API/widget tests plus isolated backend upload tests for valid, empty, unsupported, oversized, duplicate, unauthorized, failure, retry, cancellation, and multiple uploads.

### Stage C — Stage 11 extraction and worker logic

**Scope:** Validate extraction persistence, idempotency, job lifecycle, retry/backoff, stale leases, claim tokens, and cleanup without starting the real worker.

**Acceptance criteria:**

- `DocumentPage.extracted_text` is persisted and regression-tested.
- Failed and partial extraction statuses are truthful.
- Duplicate processing is prevented or explicitly versioned.
- Claim-token ownership is enforced on success/failure finalization.
- Stale jobs recover safely and retry limits/backoff are deterministic.
- OCR capability is reported accurately and missing OCR is not presented as success.

**Tests:** extractor unit tests, isolated database service tests, worker pure-function/transaction tests, capability tests. Real worker operation is blocked pending approval.

### Stage D — Stage 12 provider and consent boundary

**Scope:** Complete provider configuration, explicit consent, disclosure, normalized errors, mocked usage tracking, and health behavior.

**Acceptance criteria:**

- No provider call occurs without current explicit consent.
- UI/API identifies provider and data sent and supports decline/revocation.
- OpenAI credentials are never hardcoded or logged.
- Timeout, retry, rate-limit, auth, unavailable, and invalid structured output errors are normalized.
- Analysis never reports success after provider failure.
- Usage/token/cost fields are recorded only when actually returned or calculable.

**Tests:** mocked provider interface tests; no external provider calls during validation.

### Stage E — Stages 13–14 intelligence/evidence workspace

**Scope:** Persist versioned structured analysis, validate evidence references, and implement Flutter views for facts, dates, obligations, risks, opportunities, recommendations, unknowns, conflicts, and source navigation.

**Acceptance criteria:**

- Findings distinguish source facts, claims, inferences, assumptions, unknowns, and conflicts.
- Every important finding has valid source/page/section evidence or is explicitly unsupported/unknown.
- Users can inspect source evidence, correct/dismiss findings, provide feedback, and request re-analysis when available.
- Risk explanations include evidence, impact, uncertainty, and mitigation without presenting arbitrary scores as objective truth.

**Tests:** schema/evidence validation, ownership, correction/history, mocked analysis API, widget/navigation/error-state tests.

### Stage F — Stage 15 decisions/actions/tasks/goals

**Scope:** Connect backend actions models/services to Flutter decision, proposal approval, task, goal, milestone, and history workflows.

**Acceptance criteria:**

- Users can define decisions, criteria, options, trade-offs, assumptions, and missing information.
- Proposed actions support approve/edit/reject/dismiss; consequential actions never auto-execute.
- Tasks and goals support ownership, due dates, priorities, status, milestones, source links, and history.
- Cross-user access returns safe not-found/unauthorized behavior.

**Tests:** API ownership/transition/approval/cycle tests and Flutter form/navigation/widget tests.

### Stage G — Stage 16 tracking and notifications

**Scope:** Implement task/goal dashboards, activity, deadlines, preferences, in-app notifications, and only configured/authorized delivery channels.

**Acceptance criteria:**

- Upcoming and overdue items are timezone-aware.
- Users can disable reminders and inspect notification history.
- Delivery is reported only after the configured channel confirms it.
- No real email/SMS/external notification is sent during development validation.

**Tests:** timezone, overdue, disable, delivery-status, and widget tests using fakes.

### Stage H — Context, memory, and advanced intelligence

**Scope:** User-controlled context/memory review and safe cross-document connections.

**Acceptance criteria:**

- Persistent memory is explicitly user-approved, reviewable, correctable, and deletable.
- Temporary context is distinct from persistent memory.
- Sensitive information is not inferred or retained unnecessarily.
- Cross-document conclusions cite supporting sources and can be dismissed.

**Tests:** ownership, consent, deletion, age/source disclosure, connection evidence, and UI tests.

### Stage I — Security, privacy, and production readiness

**Scope:** Complete security review, retention/export/deletion documentation, audit events, release configuration, operations runbooks, and final reports.

**Acceptance criteria:**

- Authentication, authorization, file safety, path traversal, CORS, headers, rate limits, logs, secrets, and dependency posture are reviewed.
- Test configuration cannot target `nova_health` or an unverified real user database.
- Health/readiness, backup/restore, migration, worker, deployment, troubleshooting, user, security, and privacy documentation matches source behavior.
- No production claim is made without executed evidence.

**Tests:** approved isolated backend tests, Flutter tests, static analysis, dependency checks, and manual validation checklist. Deployment remains out of scope.

## Immediate execution batch

The first safe implementation batch after this audit is Stage 10:

1. Add an authoritative document capability/limit model or endpoint contract where the existing API can support it.
2. Replace the single-file byte-buffer UI flow with multi-selection and per-file upload state while preserving the existing `DocumentsApi` and token provider.
3. Add client-side extension/size/empty validation and clear retry/cancel/error states.
4. Add focused Flutter tests for validation, successful refresh, duplicate/server errors, network errors, retry, and cancellation behavior.
5. Review backend upload buffering and implement bounded temporary-file handling only after confirming the storage/service contract and preserving duplicate hashing.
6. Run focused Flutter tests/static analysis and isolated backend tests only; record exact results.

## Approval gates and required approval package

Before any live database or worker operation, present:

- Exact target database name, host, port, and role with credentials redacted.
- Current Alembic revision and evidence it is not `nova_health`.
- Target revision and exact expected schema changes.
- Backup and recovery plan; do not use irreversible 0008 downgrade as rollback.
- Exact command and post-operation verification.

Before external AI or notifications, present provider/channel, data scope, consent behavior, estimated cost if applicable, and exact operation. Wait for explicit approval.

## Final reporting

Create/update:

- `docs/ORVEXA_DOCUMENT_PROCESSING_RUNBOOK.md`
- `docs/ORVEXA_PRODUCTION_READINESS_REPORT.md`
- `docs/ORVEXA_USER_GUIDE.md`
- `docs/ORVEXA_OPERATIONS_RUNBOOK.md`
- `docs/ORVEXA_SECURITY_AND_PRIVACY.md`
- `docs/ORVEXA_FINAL_COMPLETION_REPORT.md`

The completion report must list exact files changed, actual test/static-analysis commands and outcomes, database implications, API/Flutter changes, completed/partial/blocked stages, external dependencies, manual validation, required approvals, and commands to run the application. No stage may be marked `COMPLETE — VERIFIED` without executed evidence.
