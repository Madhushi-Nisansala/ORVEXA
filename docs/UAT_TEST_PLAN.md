# ORVEXA User Acceptance Test Plan

## 1. Purpose

This plan defines acceptance coverage for ORVEXA user-facing workflows and their ownership/security boundaries. It covers Register, Login, Dashboard, Documents, AI Analysis, Insights, Tasks, Goals, Memory, and Search, including normal flows, invalid input, loading/empty/success/error states, navigation, persistence, isolation, and responsive layouts.

A test may be marked **PASS** only when the described workflow was executed against a running target using permitted test accounts and real application data. Source inspection, unit tests, mocked responses, and unavailable browser/device execution are evidence but are not substitutes for interactive UAT.

## 2. Scope and environment

- Desktop: current supported Google Chrome at a representative desktop viewport.
- Mobile: current supported mobile browser or Chrome device emulation at a representative narrow viewport.
- Backend: running ORVEXA API with a disposable/local database and migrations applied.
- Accounts: two newly created UAT accounts, `UAT-A` and `UAT-B`, with unique non-production email addresses. Never use production users or production documents.
- Data: documents and records created during UAT only. Do not use mock responses to claim a successful workflow.
- Evidence: record timestamps, account, environment, request/record identifier where safe, and screenshots for visual failures. Do not include passwords, tokens, or sensitive document contents in evidence.

## 3. Preconditions and execution rules

1. Confirm the target API URL, build/version, browser versions, viewport sizes, and database/environment are recorded.
2. Apply migrations and verify the service health/readiness endpoints.
3. Create `UAT-A` and `UAT-B` through the Register screen. Verify email/verification requirements as configured by the target environment.
4. Use a disposable text/PDF document owned by each account. Do not upload production data.
5. Execute each case independently unless a prerequisite is listed.
6. Record **PASS**, **FAIL**, or **BLOCKED**. Use **BLOCKED** for unavailable environments, unimplemented features, or cases not actually executed. Never convert BLOCKED to PASS based on source code.
7. On failure, record reproducible steps, expected result, actual result, and screenshot/reference if possible.

## 4. Test cases

The matrix contains 36 cases.

### Authentication and account access

| ID | Test case and procedure | Expected result |
|---|---|---|
| AUTH-01 | Register UAT-A with valid unique email, full name, and valid password. | Account is created, a clear success/verification state is shown, and the user can continue to Login as configured. |
| AUTH-02 | Register with missing required fields, malformed email, weak/mismatched password, and duplicate email. | Submission is prevented or rejected with field-level, user-friendly messages; no unintended account is created. |
| AUTH-03 | Log in as UAT-A with valid credentials. | Login succeeds and navigates to Dashboard. |
| AUTH-04 | Log in with unknown email, wrong password, blank fields, and malformed email. | Login fails safely with a user-friendly message; no protected content is shown. |
| AUTH-05 | Open a protected route while signed out, then log out from an authenticated session. | User is redirected to Login and protected content is unavailable. |
| AUTH-06 | Log in again after logout. | Authentication succeeds and previously persisted UAT-A records are available. |

### Dashboard and navigation

| ID | Test case and procedure | Expected result |
|---|---|---|
| DASH-01 | Open Dashboard after Login. | Welcome/user identity and implemented dashboard sections render without errors. |
| DASH-02 | Exercise Dashboard links to Documents, Tasks, Goals, Memory, Settings/status, and available analysis/insight entry points. | Each implemented link reaches the correct screen; back navigation and refresh behave consistently. |
| DASH-03 | Observe Dashboard during initial load, with empty account data, and after data exists. | Loading, empty, and populated states are understandable and do not show stale data. |
| DASH-04 | Force API unavailable/unauthorized response while loading Dashboard. | Error state is visible, actionable, and does not expose a stack trace or leave an infinite spinner. |

### Documents

| ID | Test case and procedure | Expected result |
|---|---|---|
| DOC-01 | Open Documents with no documents. | Empty state explains how to add a document. |
| DOC-02 | Upload a permitted disposable text/PDF document as UAT-A. | Upload completes with clear success/progress feedback and the document appears in the list. |
| DOC-03 | Submit unsupported extension/MIME type, empty file, malformed PDF, oversized file, and invalid filename/path. | Upload is rejected with a friendly reason; no partial/hidden record is created. |
| DOC-04 | Open document detail, refresh, return to list, and use archive/delete/retry actions where available. | Correct document state is shown, navigation works, and destructive actions are clear and safe. |
| DOC-05 | Exercise document list loading, empty, success, unauthorized, and network/server-error states. | Each state is visually distinct and actionable. |
| DOC-06 | Attempt to open UAT-A document using UAT-B, including direct detail URL/identifier. | UAT-B cannot read, modify, archive, or delete UAT-A data; response/UI is safe and non-disclosing. |

### AI Analysis and Insights

| ID | Test case and procedure | Expected result |
|---|---|---|
| AI-01 | From an uploaded document, start AI Analysis and observe queued/in-progress/completed states. | Analysis action is available only when prerequisites are met; progress and completion are understandable. |
| AI-02 | Attempt analysis before extraction, with missing/invalid document, and after provider/service failure. | Action is rejected or fails with a user-friendly explanation and retry path; no misleading success is shown. |
| AI-03 | Review completed analysis facts, dates, obligations, requirements, risks, and evidence. | Results are associated with the correct document and are readable and navigable. |
| INS-01 | View document Insights in loading, empty, populated, and error states. | Insight state is accurate, understandable, and tied to the selected document. |
| INS-02 | Delete an insight where supported, refresh, and attempt cross-account access. | Deletion persists and UAT-B cannot access UAT-A insights. |

### Tasks and Goals

| ID | Test case and procedure | Expected result |
|---|---|---|
| TASK-01 | Create a task with valid title/details, view it, edit it, change status/priority, and delete it if supported. | Valid task lifecycle completes and state persists after refresh. |
| TASK-02 | Submit a task with blank/invalid required values, invalid dates/status/priority, and excessively long input. | Validation is clear and no invalid task is persisted. |
| TASK-03 | Search/filter tasks, then exercise loading, empty, success, and API error states. | Search/filter results are correct and each state is actionable. |
| GOAL-01 | Create, open, edit, complete/update, and delete a goal using valid values. | Valid goal lifecycle completes and state persists after refresh. |
| GOAL-02 | Submit blank/invalid goal values and invalid dates/targets. | Validation is clear and no invalid goal is persisted. |
| GOAL-03 | Search/filter goals and exercise loading, empty, success, and error states. | Search/filter results are correct and each state is actionable. |

### Memory and Search

| ID | Test case and procedure | Expected result |
|---|---|---|
| MEM-01 | Create valid memory/context, list it, search/filter it, edit it, confirm/reject if available, archive it, and permanently delete it where supported. | Lifecycle state changes are clear and persist after refresh. |
| MEM-02 | Submit blank/invalid memory content/category and unauthorized identifiers. | Invalid input is rejected clearly; other users' memory is not disclosed. |
| MEM-03 | Use global Search with valid terms, no-match terms, blank/whitespace terms, and invalid limits/offsets. | Results are relevant, empty results are clear, and invalid requests show friendly validation. |
| MEM-04 | Search as UAT-B for UAT-A document/task/goal/memory terms and direct identifiers. | No UAT-A records appear in results or detail views. |

### Persistence and responsive acceptance

| ID | Test case and procedure | Expected result |
|---|---|---|
| PERS-01 | As UAT-A, create at least one valid record in each available feature, log out, close/reopen the app/browser, and log in again. | Records remain available to UAT-A with correct statuses and relationships. |
| PERS-02 | Repeat a representative persistence check with UAT-B. | UAT-B sees only UAT-B records; UAT-A records remain isolated. |
| RESP-01 | Execute AUTH-03, DASH-01, DOC-02, AI-01/03, TASK-01, GOAL-01, MEM-01, and MEM-03 at desktop Chrome width. | No clipping, overlap, inaccessible controls, or broken navigation. |
| RESP-02 | Repeat the same representative workflows at mobile browser width/orientation. | Layout reflows, controls remain usable, scrolling works, and no horizontal overflow blocks the workflow. |
| RESP-03 | Capture loading, empty, success, and error states at both widths. | State messaging and actions remain readable and usable. |

## 5. Exit criteria

- All executable cases have an actual result and PASS/FAIL/BLOCKED status.
- No critical/high defect remains open for authentication, authorization/isolation, data loss, or destructive actions.
- Persistence and two-account isolation are demonstrated against the target environment.
- Desktop and mobile representative workflows are executed and evidenced.
- Product owner accepts all remaining defects and explicitly accepts any BLOCKED/not implemented scope.
