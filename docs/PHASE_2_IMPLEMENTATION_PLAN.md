# ORVEXA Phase 2 Implementation Plan

## Scope

Phase 2 adds the database and authentication foundation only. It includes PostgreSQL schema management, SQLAlchemy models, secure account and session APIs, profile management, RBAC foundations, Flutter authentication integration, automated tests, and verification documentation. Document intelligence, AI analysis, trust and safety, and personal action features remain out of scope.

## Architecture

- **Backend:** FastAPI under `backend/app`, with versioned routes under `/api/v1`.
- **Persistence:** SQLAlchemy 2.x async sessions with PostgreSQL/asyncpg, UUID identifiers, UTC-aware timestamps, and Alembic migrations.
- **Security:** Argon2id password hashing, signed short-lived JWT access tokens, opaque cryptographically random refresh tokens stored only as hashes, rotation and revocation in database transactions, and backend-enforced role dependencies.
- **Client:** Existing Flutter Material 3, Dio, Riverpod, and GoRouter architecture. The backend remains the authentication source of truth. Passwords are never persisted. Mobile token storage uses secure storage when available; Web storage limitations are documented rather than hidden.

## Database design

Tables:

- `users`: normalized unique email, password hash, safe profile fields, account status, verification state, and UTC audit timestamps.
- `roles`: extensible role names (`user`, `admin`).
- `user_roles`: composite primary key and foreign keys preventing duplicate assignments.
- `refresh_tokens`: hashed opaque tokens, expiry/revocation metadata, rotation linkage, device metadata, and indexes for lookup and session revocation.

Foreign keys use deliberate deletion behavior. User deletion is restricted rather than silently cascading important account/session data. Refresh-token rows may be revoked in bulk for logout-all. Password hashes and raw tokens are never returned or logged.

## API design

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/logout-all`
- `GET /api/v1/auth/me`
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`

Responses use safe Pydantic schemas. Invalid credentials use generic errors. Registration leaves `is_verified=false` because no email delivery provider is configured. Client-submitted roles and administrative fields are rejected or ignored.

## Security considerations

- Secrets and token lifetimes come from environment-backed settings; no real secret is committed.
- JWT validation fixes the configured algorithm and validates token type, subject, expiry, issued-at, and token ID.
- Refresh tokens are hashed with a one-way digest and rotated atomically. Reuse of a revoked token is rejected and can revoke the affected session family.
- CORS is allow-list based and configurable. Authentication endpoints use a development-safe in-process rate-limit fallback; production deployments should use a shared Redis or gateway-backed limiter.
- Error responses avoid account enumeration and internal stack traces. Authorization is enforced on the backend, never by Flutter route visibility alone.
- Web refresh-token storage is not treated as equivalent to mobile secure storage. If HttpOnly SameSite cookies are not wired into the existing client, the limitation is recorded explicitly.

## Implementation order

1. Record this plan before code changes.
2. Extend backend dependencies and environment configuration.
3. Implement models, metadata registration, Alembic configuration, and the initial reversible migration.
4. Implement password, JWT, refresh-session, authentication dependency, and role services.
5. Implement authentication and profile APIs with validation and transactions.
6. Add backend tests using isolated test dependencies and mark PostgreSQL runtime checks blocked if unavailable.
7. Add Flutter auth API/repository/state abstractions, screens, routing, and token storage boundaries.
8. Add Flutter tests and run static analysis/build verification.
9. Run all available migration, backend, frontend, and regression commands.
10. Update schema, implementation, progress, README, and final verification reports with actual evidence.

## Testing strategy

- Unit tests cover password hashing/verification, JWT validation, refresh-token state transitions, and request validation.
- API tests cover registration, duplicate email handling, login, refresh rotation/reuse, logout, logout-all, current user, profile updates, unauthorized access, and RBAC.
- Flutter tests cover form validation, visibility controls, repository error mapping, auth state transitions, logout, and route behavior using controlled dependencies.
- PostgreSQL migration and integration tests run only against an isolated test database. If the environment cannot connect, the exact commands and blocker are recorded as BLOCKED rather than simulated as passed.
- Existing Phase 1 tests and health behavior are rerun to detect regressions.
