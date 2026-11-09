# ORVEXA Phase 1 Project Setup

This guide covers the current foundation only. Authentication, user management, uploads, document intelligence, AI analysis, and other later-phase features are intentionally out of scope.

## Prerequisites

- Windows 11 development environment
- Python 3.13 or compatible Python 3.x
- Flutter stable and Dart
- PostgreSQL 17 for local backend readiness checks, or Docker Desktop for the Compose setup
- Docker Desktop is required for container validation and runtime checks

## Environment

1. Copy `.env.example` to `.env`.
2. Replace the placeholder local PostgreSQL password with a developer-managed value.
3. Keep `.env` local; it is excluded by `.gitignore`.
4. Use only placeholder values in `.env.example` and never commit credentials.

For a host-run backend, `POSTGRES_HOST=localhost` and the `DATABASE_URL` in `.env.example` are appropriate. For Compose, the backend service receives `POSTGRES_HOST=postgres` and the database variables from `docker-compose.yml`.

## Backend

From the repository root in PowerShell:

```powershell
python -m venv backend/.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload
```

Endpoints:

- `GET /` — foundation service status
- `GET /health` — application and database health; returns 503 when the database is unavailable
- `GET /ready` — readiness; returns 503 unless PostgreSQL is reachable
- `/docs` — FastAPI OpenAPI documentation

Run backend checks:

```powershell
backend\.venv\Scripts\python.exe -m compileall -q backend/app backend/tests
backend\.venv\Scripts\python.exe -m pytest -q backend
```

## Flutter

From `frontend/`:

```powershell
flutter pub get
flutter analyze
flutter test
flutter build web
flutter run
```

The project includes Android, iOS, and Web scaffolding. iOS build execution requires macOS/Xcode; Android license and SDK configuration may require local Flutter doctor remediation.

## PostgreSQL and Compose

Start PostgreSQL locally with the developer-managed service, or use Docker Desktop:

```powershell
docker compose config
docker compose up --build
docker compose ps
```

Do not remove the `orvexa-postgres-data` volume during normal development. The Compose backend waits for the PostgreSQL health check and connects to the service name `postgres`.

At the time of the Phase 1 verification, Docker, `psql`, and `pg_isready` were unavailable in the verification shell, so those runtime instructions remain environment-dependent and must be rerun after installing/starting the required tools.
