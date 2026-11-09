# ORVEXA

**Understand More. Act Smarter.**

ORVEXA is a FastAPI and Flutter application for document context, extraction, and analysis.

## Release status

**The v1.0.0 release candidate is not ready for production.** The final verification report and UAT results identify unresolved Flutter test/analyzer failures, an unapplied database migration, unavailable real-provider AI configuration, incomplete interactive UAT, and unverified production deployment and recovery controls. Do not deploy, tag, push, or publish v1.0.0 based on this repository state.

See [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) for the evidence, release gates, known limitations, rollback instructions, and draft GitHub release notes.

Implemented and validated in part:
- FastAPI authentication, ownership-scoped document APIs, private local storage, extraction jobs, and Alembic migrations.
- Flutter client with secure mobile token storage and compile-time API configuration.
- PostgreSQL/pgvector Compose configuration and a separate production-oriented Compose path.
- Backend automated coverage and release/deployment documentation.

Production deployment, managed object storage, production TLS/reverse proxy, real AI provider verification, monitoring, and backup/recovery remain operator-controlled or incomplete.

## Prerequisites

- Python 3.13 or compatible Python 3.x.
- Flutter stable and Dart.
- Docker Desktop or Docker Engine for local containers.

## Local setup

1. Follow [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) and copy the environment template without committing secrets.
2. Install backend requirements: `python -m pip install -r backend/requirements.txt`.
3. Run the backend: `uvicorn app.main:app --app-dir backend --reload`.
4. Run backend tests: `python -m pytest backend/tests -q`.
5. Fetch Flutter packages and test: `cd frontend; flutter pub get; flutter test`.
6. Run the Flutter app: `cd frontend; flutter run`.
7. With Docker installed, start local services with `docker compose up --build`.

## Project structure

```text
backend/       FastAPI service and tests
frontend/      Flutter client and widget tests
docs/          Architecture, security, API, testing, and delivery documentation
ORVEXA/        Existing .NET 10 baseline project; untouched in Phase 1
```

## Documentation

- [User Guide](docs/USER_GUIDE.md) — current user workflows and known limitations.
- [Release Checklist](docs/RELEASE_CHECKLIST.md) — release gates, readiness decision, rollback, and GitHub release draft.
- [Deployment](docs/DEPLOYMENT.md) — operator deployment runbook; does not deploy automatically.
- [Production Configuration](docs/PRODUCTION_CONFIGURATION.md) — required runtime configuration and secret handling.
- [Backup and Restore](docs/BACKUP_AND_RESTORE.md) — backup scope, restore drill, and recovery procedure.
- [Final Verification Report](docs/FINAL_VERIFICATION_REPORT.md) and [UAT Results](docs/UAT_TEST_RESULTS.md) — reviewed release evidence.
- [Architecture](docs/ARCHITECTURE.md), [Security](docs/SECURITY.md), and [Testing](docs/TESTING.md) — engineering references.

Do not commit populated `.env` files, secrets, database dumps, build artifacts, logs, or temporary files. No production action is performed by the local setup commands.
