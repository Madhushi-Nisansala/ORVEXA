# API Documentation

The API base path is `/api/v1`. Interactive OpenAPI is available only outside staging/production; production clients should use the versioned contract and bearer tokens.

## Public endpoints

- `GET /api/v1/health` — service health response.
- `POST /api/v1/auth/register`, `/login`, `/refresh`, `/logout` — authentication lifecycle.

## Authenticated resources

- `GET/PATCH /api/v1/users/me` and `GET /api/v1/auth/me` — current user.
- `/api/v1/documents` — upload, list, search, retrieve, extract, pages, content, archive, retry, and delete. Uploads are size-, type-, and signature-validated.
- `/api/v1/context`, `/api/v1/insights`, `/api/v1/search` — user-owned context and search operations.
- `/api/v1/tasks` and `/api/v1/goals` — user-owned action planning resources.

All resource access is ownership-scoped. Errors intentionally return safe messages and never include filesystem paths, credentials, or stack traces. Check generated OpenAPI in a non-production environment for request and response schemas.
