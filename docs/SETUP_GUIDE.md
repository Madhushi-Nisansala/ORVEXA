# Setup guide

## Prerequisites

- Python 3.13+
- Flutter stable 3.35+
- PostgreSQL 17 with pgvector, or Docker Compose

## Backend

```bash
copy backend\.env.example backend\.env  # PowerShell
python -m pip install -r backend/requirements.txt
alembic -c backend/alembic.ini upgrade head
uvicorn app.main:app --app-dir backend --reload
```

Generate `JWT_SECRET_KEY` with a password generator or `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Keep it outside source control. Configure `DATABASE_URL` or the `POSTGRES_*` variables, and set explicit `CORS_ALLOWED_ORIGINS`.

## Flutter

```bash
cd frontend
flutter pub get
flutter run --dart-define=ORVEXA_API_BASE_URL=http://localhost:8000
```

For production, provide an HTTPS API URL with `--dart-define`; do not use localhost. Mobile tokens use `flutter_secure_storage`. Web deployment must use HTTPS and an appropriate browser security policy.

## Compose

Use `docker compose up --build` for development. Use `docker compose -f docker-compose.prod.yml up -d --build` only after supplying a production secret file and configuring external backups, TLS termination, monitoring, and a private storage backup.
