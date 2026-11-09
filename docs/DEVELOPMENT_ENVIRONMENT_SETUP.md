# ORVEXA Development Environment Setup

This guide uses only the existing project configuration and a project-local Python environment. It does not install packages globally, reset databases, or delete Docker volumes.

## 1. Open the repository

```powershell
Set-Location 'C:\My Projects\ORVEXA'
```

## 2. Configure local secrets

Copy `.env.example` to `.env` and replace placeholders with local development values. Never commit `.env` or paste its contents into logs or reports.

```powershell
Copy-Item .env.example .env
```

The current `.gitignore` excludes `.env` and `.env.*` while retaining `.env.example`.

## 3. Install/start Docker Desktop manually

Docker is currently **BLOCKED** on this machine: the CLI and Engine are unavailable and WSL is not installed. Install Docker Desktop from:

https://www.docker.com/products/docker-desktop/

Docker Desktop may require WSL 2, administrator permission, and a Windows restart. Do not bypass those requirements. After Docker Desktop is running, open a new PowerShell window and run:

```powershell
docker --version
docker compose version
docker info
```

## 4. Use the project Python environment

The existing `backend/.venv` is valid and uses Python 3.13.14. From the backend directory:

```powershell
Set-Location 'C:\My Projects\ORVEXA\backend'
.\.venv\Scripts\Activate.ps1
python --version
python -m pip --version
```

If activation is blocked for this PowerShell process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Do not permanently lower the execution policy. The environment can also be used without activation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 5. Validate backend dependencies and imports

```powershell
python -m pip install -r requirements.txt
python -m pip check
python -m pip show fastapi uvicorn sqlalchemy alembic pytest argon2-cffi
python -c "from app.main import app; print(app.title)"
python -m compileall .
```

The observed run installed the declared requirements and returned no broken requirements.

## 6. Validate PostgreSQL and migrations

First ensure the configured local PostgreSQL credentials are valid. The Windows PostgreSQL service was running and TCP port 5432 was reachable, but the current application credentials failed authentication.

```powershell
python -m alembic --version
python -m alembic history
python -m alembic current
python -m alembic check
```

Do not run a downgrade, drop database, reset, or volume deletion command. Do not run `alembic upgrade head` until the database URL and target database have been reviewed.

## 7. Validate Docker Compose after Docker is ready

From the repository root:

```powershell
docker compose config
docker compose up -d
docker compose ps
docker compose logs postgres --tail 30
```

Use the actual service names from `docker compose config`; the existing file currently defines `postgres` and `backend`. Never delete `orvexa-postgres-data`.

## 8. Run backend checks

```powershell
Set-Location 'C:\My Projects\ORVEXA\backend'
python -m pytest -q
python -m pytest -q -k auth
python -m pytest -q -k password
```

The current repository contains six health/configuration tests; the full run passed all six. No separate auth/password test files were present.

## 9. Run the backend server

The discovered entry point is `app.main:app`:

```powershell
python -m uvicorn app.main:app --reload
```

With the server running, check `http://127.0.0.1:8000/`, `/health`, `/api/v1/health`, `/api/v1/ready`, and `/docs`. Database-backed health/readiness requires valid PostgreSQL credentials.

## 10. Run Flutter checks

```powershell
Set-Location 'C:\My Projects\ORVEXA\frontend'
flutter pub get
flutter analyze
flutter test
flutter build web
```

The observed frontend run passed dependency resolution, analysis, all five tests, and the web build. `flutter doctor -v` reports Android licenses as unknown; run `flutter doctor --android-licenses` only if Android development is needed.
