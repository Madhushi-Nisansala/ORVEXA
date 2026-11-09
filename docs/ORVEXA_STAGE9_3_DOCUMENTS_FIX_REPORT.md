# ORVEXA Stage 9.3 — Documents Fix Report

## Status

Completed and validated with focused Flutter tests and `flutter analyze`.

## Confirmed root cause

The Documents list request was constructed as:

- `GET http://localhost:8000/documents`
- No `Authorization` header was added by the default `ApiClient()` instances used by the Documents feature.

The backend route is registered as `GET /api/v1/documents` and is protected by `get_current_user`. Therefore, the original request did not match the backend route and would return HTTP 404. If only the path were corrected, the request would still fail with HTTP 401 because the Documents client did not load the stored access token. This was confirmed by inspecting the frontend request construction and backend router registration; no live backend, database, token, or secret was accessed.

## Changes made

- Updated all Documents API paths to use `/api/v1/documents` and the corresponding `/api/v1/documents/{id}` paths.
- Added an `ApiClient` access-token provider interceptor. It reads the access token from secure storage at request time and adds `Authorization: Bearer ...` without logging or exposing the value.
- Updated Documents list, upload, archive, delete, extraction, analysis, and detail requests to use authenticated clients.
- Kept loading, successful empty, successful populated, and error states separate.
- Added safe error messages for unauthorized, server, timeout, connection, and unknown failures without displaying exception details or credentials.
- Disabled Riverpod's automatic provider retries for the Documents list so the error state remains stable and the visible Retry button is deterministic. Retry invalidates the provider and repeats the request.
- Changed Dashboard-to-Documents navigation to `push`.
- Added a visible Documents AppBar Back button. It pops normal navigation history and falls back to `/dashboard` when no history exists.
- Changed document tile navigation to `push`, preserving detail navigation and normal back behavior.

## Files changed

- `frontend/lib/core/network/api_client.dart`
- `frontend/lib/features/documents/data/documents_api.dart`
- `frontend/lib/features/documents/presentation/documents_screen.dart`
- `frontend/lib/features/documents/presentation/document_detail_screen.dart`
- `frontend/lib/features/dashboard/presentation/dashboard_screen.dart`
- `frontend/test/documents_test.dart`

## Validation

Focused command:

```text
flutter test test/documents_test.dart
```

Result: **Passed — 7 tests**.

Coverage includes:

1. Empty API response.
2. Populated API response and parsing.
3. Unauthorized response.
4. Network error.
5. Retry repeating the request.
6. Back navigation returning to Dashboard.
7. Document detail navigation.

Analyzer command:

```text
flutter analyze
```

Result: **Passed — No issues found!**

## Limitations

- Validation used mocked Dio/API responses only, as required.
- No live HTTP request was made, and no PostgreSQL connection, migration, document worker, AI provider, `nova_health`, `.env`, password, or token value was accessed.
- Backend route confirmation was static source inspection rather than live-server verification.
