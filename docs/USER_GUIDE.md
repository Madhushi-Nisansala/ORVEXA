# ORVEXA User Guide

ORVEXA helps users submit documents and manage the context, tasks, goals, and insights associated with them. This guide describes the intended current workflow. Availability of a feature depends on the deployed frontend build, backend configuration, and enabled AI provider.

## Before you begin

- Use the HTTPS application URL supplied by your administrator.
- Do not use a local development URL or share your password, access token, documents, or private links.
- Use only documents you are authorized to upload and process.
- Contact the administrator if the application reports an unavailable analysis provider, service outage, or storage error.

## Account access

1. Open the ORVEXA application.
2. Select **Register** and enter the requested account information, or select **Sign in** for an existing account.
3. After successful authentication, continue to the Dashboard.
4. Use **Log out** when finished, especially on shared devices.
5. If a session expires, sign in again. Do not retry repeatedly if the service reports an outage.

The application is designed to keep records scoped to the signed-in account. Do not assume that a record was saved until it appears after a refresh or re-login.

## Dashboard

The Dashboard is the starting point for the available feature areas, including Documents, Tasks, Goals, Memory, and service status. A loading indicator means data is still being retrieved; an error message should identify a retry or administrator action where supported.

Some builds may show sections marked **Coming soon**. Those sections are not available workflows and should not be treated as completed product features.

## Documents

### Upload a document

1. Open **Documents**.
2. Choose the upload action.
3. Select a supported document from your device.
4. Confirm the upload and wait for the document to appear in the list.
5. Open the document to review its processing status.

Use a normal filename and an approved file type. Uploads can be rejected for unsupported extensions or MIME types, malformed content, empty files, excessive size, or unsafe paths. Never rename an unsafe or untrusted file to bypass validation.

### Review and manage a document

Open a document to view its metadata, extraction/analysis status, evidence, and available insights. Depending on the build and record state, you may be able to refresh processing, archive, delete, or retry a failed operation. Confirm destructive actions before continuing.

If a document is missing after upload, shows an error, or remains in a processing state, refresh once and contact the administrator with the document identifier and approximate time. Do not upload sensitive duplicates while investigating.

## Analysis and insights

Analysis may be queued and progress through processing states before results are available. When complete, review facts, dates, obligations, requirements, risks, and supporting evidence rather than relying on a generated summary alone.

Analysis requires a configured provider. A deployment using the unavailable provider cannot produce verified real-provider results. Provider errors should be treated as retryable only when the application offers a retry action; otherwise contact the administrator.

## Tasks and goals

Use the available **Tasks** and **Goals** areas to create, review, update, and complete personal records. Validate the title, status, progress, dates, and dependencies before saving. Refresh the list after changes and confirm that the record remains after logging out and back in.

If an area is marked **Coming soon** or is absent from the deployed navigation, it is not currently available in that deployment.

## Memory and search

Use **Memory** where available to record, review, archive, or permanently delete context. Permanent deletion should be treated as irreversible.

Backend search capabilities exist, but a dedicated global Search screen was not confirmed in the reviewed Flutter routes. Do not assume that a search feature is available in the user interface; use the navigation exposed by the deployed build.

## Privacy and account isolation

ORVEXA is designed to enforce ownership checks on backend records. Do not attempt to access another user's identifiers or documents. Report any record that appears to belong to another account immediately and do not modify it.

## Troubleshooting

| Problem | Safe action |
| --- | --- |
| Cannot sign in | Check the application URL and credentials once, then contact the administrator if the service remains unavailable. |
| Page keeps loading | Refresh once. If it persists, record the page, time, and visible error; do not repeatedly submit forms. |
| Upload rejected | Check type, size, content, and filename. Do not bypass validation by changing extensions. |
| Analysis unavailable | Confirm the document is processed, then contact the administrator; the provider may not be configured. |
| Record disappears | Refresh and sign in again. Report the record and account details without sharing credentials. |
| Service status is unhealthy | Stop destructive or repeated operations and contact the operator. |

## Known limitations in the reviewed build

These limitations are release-readiness findings, not user workarounds:

- The reviewed release candidate was not production-ready and interactive UAT was not signed off.
- The reviewed Flutter suite had 10 failures, including authentication and document/dashboard navigation timeouts.
- Flutter analysis reported 19 issues, including protected/test-only Riverpod access and deprecated APIs.
- Real provider-backed AI analysis and insight generation were not verified; the reviewed configuration used an unavailable provider.
- Dashboard context counts were hardcoded to zero and other dashboard totals were aggregated client-side.
- Global Search backend support exists, but a Flutter global Search route was not confirmed.
- Some Dashboard feature areas may display **Coming soon**.
- The current web build uses JavaScript; WebAssembly compatibility for the secure-storage web dependency was not available.
- Production TLS, hosting, managed object storage, monitoring, secrets, backups, and recovery are operator responsibilities and were not verified by this review.

For release and operational status, see [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md), [PRODUCTION_CONFIGURATION.md](PRODUCTION_CONFIGURATION.md), and [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md).
