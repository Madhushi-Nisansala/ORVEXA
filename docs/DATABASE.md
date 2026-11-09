# Database operations

ORVEXA uses PostgreSQL with `pgvector/pgvector:pg17` for local and containerized development. The application connects through SQLAlchemy's async engine and uses configurable `DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW`, and `DATABASE_CONNECT_TIMEOUT`.

## Migrations

Run migrations from `backend/`:

```bash
alembic upgrade head
alembic current
alembic history
```

Review every migration before applying it to production. Never use `alembic downgrade`, database reset scripts, or destructive SQL against production without an approved recovery plan.

## Production roles and backups

Use a dedicated application role with only the permissions required by the schema. Keep migration privileges separate where possible. Enable encrypted, automated PostgreSQL backups with retention and test restores regularly. The application database URL, password, and backup credentials belong in the hosting secret manager, not Git.

The Compose named volume is suitable for local persistence, not a complete production backup strategy. Production operators must configure point-in-time recovery, monitoring, restore drills, and a documented RPO/RTO.
