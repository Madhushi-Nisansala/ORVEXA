# ORVEXA Production Deployment

This is a deployment preparation and operator runbook. It does not deploy ORVEXA, access hosting accounts, change DNS, run migrations against a production database, or create backups. Obtain explicit authorization and configure hosting access before performing any production step.

The reference architecture is:

```text
HTTPS browser -> static Flutter Web hosting/CDN
HTTPS API domain -> TLS reverse proxy -> FastAPI container
                                      -> private PostgreSQL/pgvector
                                      -> private durable document storage
```

PostgreSQL, document storage, and the backend container must not be directly exposed to the public internet.

## 1. Release prerequisites

Confirm these before scheduling a release:

- Backend runtime/container account and private networking.
- PostgreSQL 17-compatible provider with pgvector, TLS, backups, and a private endpoint.
- HTTPS static hosting/CDN for Flutter Web.
- Domain/DNS access for `<frontend-domain>` and `<api-domain>`.
- Secret manager access for runtime secrets and GitHub environment secrets.
- Encrypted durable document storage and a tested restore procedure.
- Monitoring, log retention, alert routing, and an on-call owner.
- Approved RPO/RTO and a completed backup/restore drill.
- Explicit production deployment authorization and a rollback owner.

Configuration values and estimated costs are listed in [PRODUCTION_CONFIGURATION.md](PRODUCTION_CONFIGURATION.md). Backup and restore operations are in [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md).

## 2. Configure production values

Create production configuration in the hosting platform, not in Git. Required values include:

```text
APP_ENV=production
DEBUG=false
API_HOST=0.0.0.0
LOG_LEVEL=INFO
CORS_ALLOWED_ORIGINS=https://<frontend-domain>
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=<generated-secret-at-least-32-bytes>
POSTGRES_DB=<database-name>
POSTGRES_USER=<application-user>
POSTGRES_PASSWORD=<provider-secret>
POSTGRES_HOST=<private-database-host>
POSTGRES_PORT=5432
DOCUMENT_STORAGE_ROOT=/app/storage/documents
```

Use a secret manager for passwords, JWT secrets, storage credentials, and AI provider keys. Do not copy `.env.example` into a production image and do not print environment variables for troubleshooting. The backend rejects production startup for a short/default JWT secret, `DEBUG=true`, wildcard CORS, or an excessive file limit.

## 3. Prepare PostgreSQL

1. Provision a private PostgreSQL 17-compatible database with pgvector support.
2. Create a dedicated least-privilege application role and database.
3. Enable provider encryption, TLS, automated backups, and point-in-time recovery where available.
4. Allow inbound database traffic only from the backend network.
5. Set the individual PostgreSQL variables or a correctly URL-encoded `DATABASE_URL`.
6. Configure pool settings for the selected runtime capacity; do not expose port 5432 publicly.

Before a migration, take or verify a fresh database backup. Migration commands run from the backend working directory:

```powershell
python -m alembic current
python -m alembic history
python -m alembic upgrade head
```

Run the upgrade once as a controlled release job. Do not run competing migration jobs from multiple backend replicas. Never reset, drop, or downgrade a production database as a rollback shortcut.

## 4. Prepare secure document storage

The repository currently implements private local storage. `docker-compose.prod.yml` mounts a named `document-storage` volume; this is durable only if the hosting platform persists and backs it up. It is not an implemented S3/object-storage adapter.

Choose and document one approved option:

- Encrypted durable volume with restricted host access and scheduled backups; or
- An implemented and tested S3-compatible provider using private objects, encryption, restricted IAM, lifecycle rules, and a documented restore path.

Do not make document objects public. Do not put storage credentials in Flutter. Validate upload, download, delete, volume capacity, and recovery before accepting production traffic.

## 5. Deploy the backend

Build the image from `backend/Dockerfile`. The image runs as a non-root `app` user and exposes port 8000. Use the production command, not the development reload command:

```text
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
```

The existing production Compose path is a reference for a single-host deployment:

```powershell
docker compose -f docker-compose.prod.yml config
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d postgres
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
docker compose -f docker-compose.prod.yml up -d backend
```

Review rendered configuration before running it. Supply the backend environment through the host secret manager rather than committing `backend/.env`. For a managed container service, run the migration as a one-off release job and configure the service health checks to use `/health` or `/ready`.

## 6. Configure HTTPS, proxy, CORS, and health checks

Terminate TLS at the managed load balancer or reverse proxy, redirect HTTP to HTTPS, enable certificate renewal, and restrict administrative access. The API application adds HSTS in production, but the proxy is responsible for certificate and redirect enforcement. Confirm that forwarded headers are trusted only from the configured proxy.

Set `CORS_ALLOWED_ORIGINS` to the exact HTTPS frontend origin, without `*` and without localhost. Verify that an allowed frontend request succeeds and an unrelated origin is rejected.

Configure monitoring checks:

- `GET https://<api-domain>/health` must return HTTP 200 only when the database is connected.
- `GET https://<api-domain>/ready` must return HTTP 200 only when the service is ready.
- Alert on HTTP 503/5xx responses, restart loops, certificate expiry, storage exhaustion, and backup failures.

Production API documentation routes are disabled by the application. Do not expose debug endpoints or database administration interfaces.

## 7. Build and publish Flutter Web

Build in CI or a trusted release environment with the real HTTPS API URL:

```powershell
cd frontend
flutter pub get
flutter analyze
flutter test
flutter build web --release `
  --dart-define=ORVEXA_PRODUCTION=true `
  --dart-define=ORVEXA_API_BASE_URL=https://<api-domain> `
  --dart-define=ORVEXA_APP_VERSION=<release-version>
```

Publish `frontend/build/web` to HTTPS static hosting/CDN. Configure SPA fallback to `index.html`, a restrictive security policy appropriate for the application, compressed assets, and cache invalidation for `index.html` on release. Verify the output contains no localhost API URL and that browser requests use HTTPS.

## 8. GitHub Actions CI/CD

The existing `.github/workflows/ci.yml` runs backend lint/tests/audit, Flutter checks, and a release Web build using the repository/environment variable `ORVEXA_API_BASE_URL`. It does not deploy.

If CI/CD is approved, add a separate protected `production` environment and a deployment job only after selecting the hosting provider. Use short-lived provider credentials or an OIDC trust relationship where supported. Store deployment credentials and API values in GitHub environment secrets/variables, require approval, and restrict the job to reviewed tags or the protected default branch. Keep migrations as an explicit, auditable release step rather than hiding them in an uncontrolled startup loop.

Required CI release gates:

1. Backend tests, Ruff, and `pip-audit` pass.
2. Flutter format, analyze, tests, and HTTPS Web build pass.
3. Image vulnerability scan and provider deployment dry run pass.
4. Backup is verified and migration SQL/revisions are reviewed.
5. Production approval is recorded.

## 9. Smoke test and rollback

After deployment, verify DNS/TLS, `/health`, `/ready`, authentication, CORS, document upload/download/delete, logs, metrics, and alert delivery. Confirm no secrets appear in logs or client assets.

For application-only failures, route traffic to the previous compatible image. Do not automatically roll back a database migration. Confirm schema compatibility before image rollback; if data recovery is required, follow [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md) and never delete or reset existing production data.

## 10. Final go/no-go checklist

- [ ] Hosting accounts, domains, owners, and costs are approved.
- [ ] Production secrets are injected by a secret manager and are not in Git.
- [ ] No production setting contains localhost, wildcard CORS, or development reload behavior.
- [ ] HTTPS redirect, certificate renewal, HSTS, and secure proxy forwarding are verified.
- [ ] PostgreSQL is private, backed up, and migration state is recorded.
- [ ] Document storage is private, durable, capacity-monitored, and restorable.
- [ ] Flutter Web points to the HTTPS API domain.
- [ ] Health checks, logs, metrics, and alerts are working.
- [ ] CI release gates and production approval are configured.
- [ ] Explicit authorization to deploy has been recorded.
