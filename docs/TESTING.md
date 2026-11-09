# Testing

The repository includes backend pytest coverage and Flutter tests. CI runs linting, tests, dependency auditing, Flutter analysis, formatting, and a release Web build.

Run locally:

```bash
python -m pytest backend/tests -q
cd frontend; dart format --output=none --set-exit-if-changed lib test; flutter analyze; flutter test
cd frontend; flutter build web --release --dart-define=ORVEXA_PRODUCTION=true --dart-define=ORVEXA_API_BASE_URL=https://api.example.test
cd backend; alembic check
```

Add integration coverage for cross-user access, migrations against PostgreSQL, uploads, AI provider failures, backups/restores, accessibility, and critical end-to-end journeys before a high-risk release.

Never report a test as passed without executing it in the target environment.
