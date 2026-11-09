# ORVEXA Production Configuration

This document is the production configuration contract for ORVEXA. It is provider-neutral by design: replace the placeholders with values from the selected hosting providers. Do not commit a populated `.env`, paste secrets into tickets, or expose backend secrets to Flutter.

## Required hosting resources

| Resource | Required configuration | Owner |
| --- | --- | --- |
| Backend runtime | Container/VPS/PaaS running `backend/Dockerfile`, private networking, restart policy | Platform operator |
| PostgreSQL | PostgreSQL 17-compatible database with pgvector support, TLS, backups, and private access | Database operator |
| Frontend hosting | HTTPS static hosting/CDN for `frontend/build/web` | Frontend operator |
| DNS/TLS | DNS records and managed certificate for the frontend and API domains | DNS operator |
| File storage | Encrypted persistent volume for the current provider, or an implemented S3-compatible adapter | Storage operator |
| Secret manager | Runtime injection for database, JWT, storage, and provider credentials | Security operator |
| Monitoring | Log retention, uptime checks, and alert notifications | Operations operator |

Estimated small-production costs are normally: domain $10–30/year, backend $5–50/month, managed PostgreSQL $15–100+/month, static hosting $0–30/month, object storage $1–20+/month plus transfer, and monitoring $0–50/month. Obtain current provider quotes before approval.

## Environment separation

### Development

Use the repository `.env.example` and `backend/.env.example` as templates only. Development may use localhost endpoints, local PostgreSQL, a development JWT secret, and `APP_ENV=development`. The root `docker-compose.yml` intentionally uses a reload server and publishes local ports.

### Production

Use `APP_ENV=production` and inject values through the hosting platform's secret/configuration mechanism. Do not use the development `.env` files as production files without replacing every value and removing localhost endpoints.

Required production baseline:

```text
APP_ENV=production
DEBUG=false
API_HOST=0.0.0.0
LOG_LEVEL=INFO
CORS_ALLOWED_ORIGINS=https://<frontend-domain>
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=<generated-secret-at-least-32-bytes>
POSTGRES_DB=<managed-database-name>
POSTGRES_USER=<managed-database-user>
POSTGRES_PASSWORD=<managed-database-password>
POSTGRES_HOST=<private-database-host>
POSTGRES_PORT=5432
DOCUMENT_STORAGE_ROOT=/app/storage/documents
```

Use either `DATABASE_URL` supplied by the database provider or the individual PostgreSQL variables. If a password contains URL-reserved characters, prefer the individual variables or ensure the URL is correctly encoded. Never print the resulting URL in logs.

The application rejects production/staging startup when `DEBUG=true`, the JWT secret is missing/short, CORS contains `*`, or the configured file limit is over 100 MiB.

## Domain and API configuration

Choose and record values before deployment:

```text
Frontend: https://<frontend-domain>
API:      https://<api-domain>
CORS:     https://<frontend-domain>
```

Build Flutter Web with the production API URL. The URL is compile-time configuration and must not be a localhost URL:

```powershell
flutter build web --release `
  --dart-define=ORVEXA_PRODUCTION=true `
  --dart-define=ORVEXA_API_BASE_URL=https://<api-domain> `
  --dart-define=ORVEXA_APP_VERSION=<release-version>
```

Verify the generated deployment contains no `http://localhost`, `127.0.0.1`, or development API URL. The Flutter client does not receive database, JWT, object-storage, or AI provider credentials.

## FastAPI runtime

Use the production container path, not the development reload command:

```text
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
```

Run migrations as a controlled release step before routing traffic. Run one migration job at a time. Use multiple application workers only after validating memory usage and the background extraction/worker model; do not blindly duplicate worker processes that claim the same jobs.

The API disables OpenAPI documentation in production/staging. The application supplies security headers and HSTS, but HTTPS termination, redirect behavior, certificate renewal, and secure proxy forwarding must be configured and tested at the reverse proxy/hosting layer.

## PostgreSQL

Use a managed PostgreSQL service where possible. Require:

- Private network access from the backend.
- TLS in transit and encrypted storage.
- A dedicated least-privilege application role.
- Automated provider backups and point-in-time recovery where available.
- Connection limits sized for the runtime (`DATABASE_POOL_SIZE` and `DATABASE_MAX_OVERFLOW`).
- pgvector support if vector features are enabled.

Do not publish port 5432 publicly. Test `/health` and `/ready` after database changes; both return HTTP 503 when the database cannot be reached.

## Secure file storage

The implemented provider is `LocalStorageProvider`, rooted at `DOCUMENT_STORAGE_ROOT`, with path traversal protection and private files. In the current `docker-compose.prod.yml`, this is a named Docker volume. It is not a highly available object-storage integration.

For production, choose one of these explicitly:

1. Use an encrypted, durable, access-controlled persistent volume and back it up according to [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md).
2. Implement and test an S3-compatible storage provider before switching to a bucket. Use private objects, server-side encryption, restricted IAM credentials, lifecycle rules, and presigned URLs or backend-mediated downloads.

Do not make document files publicly readable. Do not place storage credentials in Flutter. Record the storage recovery procedure and test it before accepting production documents.

## JWT and secret management

Generate a unique secret outside the repository, for example:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Store it in the hosting secret manager as `JWT_SECRET_KEY`. Rotate it under a planned token invalidation procedure because changing it invalidates existing JWTs. Keep `OPENAI_API_KEY` and any future storage credentials server-side. GitHub Actions should use environment-scoped secrets and protected production approvals.

## Logging and health monitoring

Set `LOG_LEVEL=INFO` initially and collect stdout/stderr centrally. Logs include timestamps, level, and logger name. Do not log authorization headers, JWT values, database URLs, document contents, or provider secrets. Set retention and access controls in the hosting platform.

Configure:

- Liveness check: `GET /health` (HTTP 200 only when the database is reachable).
- Readiness check: `GET /ready` (HTTP 200 only when ready to receive traffic).
- External uptime check against the HTTPS API domain.
- Alerts for repeated 5xx responses, failed readiness, container restarts, storage exhaustion, backup failure, and certificate expiry.

## Preflight acceptance checks

- `APP_ENV=production` and `DEBUG=false` are confirmed in the runtime.
- No production configuration contains localhost or wildcard CORS.
- API and frontend resolve only over HTTPS.
- CORS allows the exact frontend origin and rejects an unapproved origin.
- PostgreSQL is private and `/health` plus `/ready` are passing.
- Migrations have been reviewed and applied once.
- Document upload/download/delete works through private storage.
- Backup and restore have been tested in an isolated environment.
- Logs and alerts are visible to the on-call operator.
