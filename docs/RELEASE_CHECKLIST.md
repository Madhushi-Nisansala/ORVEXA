# ORVEXA v1.0.0 Release Checklist

**Review date:** 2026-11-10  
**Release candidate:** v1.0.0  
**Decision:** **NOT READY — do not recommend v1.0.0**  
**Scope:** Release documentation and readiness review only. No deployment, migration, backup, tag, push, or publication was performed.

## Decision summary

The release criteria are not met. The final verification report records six critical/high blockers, and UAT is not signed off. The repository has no Git commits, so there is no verified release commit to tag. v1.0.0 must not be tagged, published, or deployed until every blocker below has objective evidence and QA/product approval.

## Evidence reviewed

| Evidence | Result | Release impact |
| --- | --- | --- |
| [Final verification report](FINAL_VERIFICATION_REPORT.md) | **Not production-ready** | Authoritative blockers remain |
| [UAT test results](UAT_TEST_RESULTS.md) | **Not signed off** | Real browser/device and real-account workflows were unavailable |
| [Production configuration](PRODUCTION_CONFIGURATION.md) | Contract exists | External production values and secret-manager setup remain unverified |
| [Backup and restore](BACKUP_AND_RESTORE.md) | Procedure exists | Backup configuration and isolated restore drill remain unverified |
| Git history/status | No commits; working tree is untracked | No intended release commit exists |

## Release gates

### Verification and defect closure

- [x] Backend automated suite evidence reviewed: 83 passed, 1 skipped with an ephemeral JWT secret.
- [ ] Backend default-environment test collection works without manual secret injection.
- [ ] All 10 Flutter test failures are fixed and the complete suite passes.
- [ ] Flutter analyzer reports zero release-blocking issues; protected/test-only access and deprecated APIs are resolved.
- [ ] Dashboard context counts are authoritative and dashboard aggregation is appropriately bounded.
- [ ] Real AI provider credentials/model are configured in a secret manager and provider-backed analysis/insights pass with safe fixtures.
- [ ] Dependency vulnerability scan is installed, executed, reviewed, and meets policy.
- [ ] Product owner has resolved the Global Search UI scope and Dashboard “Coming soon” scope.

### Database and migration safety

- [ ] A production-equivalent isolated database with pgvector is provisioned.
- [ ] `alembic current` and `alembic check` confirm the target is at migration head `0011_global_search_indexes`.
- [ ] A fresh verified backup exists before migration.
- [ ] Migration review and a single controlled `alembic upgrade head` are approved and recorded.
- [ ] Post-migration `/health` and `/ready` checks return HTTP 200.

Current blocker: the reviewed target database was behind migration head. No migration was run during verification.

### UAT and product acceptance

- [ ] Disposable isolated UAT deployment is available.
- [ ] UAT-A and UAT-B registration/login, persistence, logout/re-login, and cross-account isolation pass.
- [ ] Desktop Chrome and mobile-width representative workflows pass.
- [ ] Document upload, invalid upload, detail, archive/delete, retry, and error states pass.
- [ ] Real provider-backed analysis and insights pass with permitted test data.
- [ ] Tasks, goals, memory, and search acceptance passes or has documented product scope approval.
- [ ] All FAIL cases have reproducible defect records and closure evidence.
- [ ] QA and product-owner sign-off is recorded.

Current blocker: interactive UAT was unavailable; AUTH-03 and DOC-04 failed in Flutter tests, while the remaining interactive cases are blocked rather than passed.

### Production deployment health

- [ ] Production domains, TLS termination, redirect behavior, proxy forwarding, and exact CORS origin are configured.
- [ ] Backend runs with `APP_ENV=production`, `DEBUG=false`, a generated JWT secret, and secret-manager injection.
- [ ] Frontend release is built with the production HTTPS API URL and contains no localhost/development URL.
- [ ] Backend, database, storage, and admin interfaces are not publicly exposed.
- [ ] Monitoring, log retention, alert routing, restart-loop alerts, certificate alerts, storage alerts, and backup alerts are active.
- [ ] Post-deployment smoke tests pass: health, readiness, registration/login, protected route, document lifecycle, and logout.
- [ ] Production health evidence includes timestamp, deployment identifier, environment, URLs checked, and responsible operator.

Current status: no production deployment or production health check was available to review.

### Backup, recovery, and rollback

- [ ] RPO, RTO, retention, geographic requirements, backup owner, and restore approver are recorded.
- [ ] PostgreSQL backups/PITR include schema, data, extensions, and pgvector state.
- [ ] Private document storage is backed up separately from PostgreSQL.
- [ ] An isolated restore drill verifies database storage keys resolve to restored document files.
- [ ] Restored `/health`, `/ready`, authentication, document listing, upload, download, and deletion pass.
- [ ] Recovery evidence and checksums are retained outside the repository.

Follow [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md). Do not downgrade production as a routine rollback; restore known-good database and document backups under an approved recovery plan.

## Security and repository hygiene

- [x] Root `.gitignore` ignores `.env` files and preserves only example templates.
- [x] Release documentation does not reproduce secret values.
- [ ] Review `git diff --cached` and `git ls-files` before the first release commit.
- [ ] Confirm no secrets, populated `.env` files, database dumps, SQL exports, build output, logs, or temporary files are tracked.
- [ ] Rotate any local credential that was shared, logged, committed elsewhere, or used outside disposable development.
- [ ] Confirm production secrets are supplied only by the hosting secret manager.

## Intended release commit and tag

No release commit currently exists: `git log` reports that the repository has no commits. After all gates pass:

1. Review and stage only the intended source and documentation files.
2. Confirm `git status --short`, `git diff --cached --check`, and secret/artifact scans are clean.
3. Create the approved commit using the repository's agreed commit convention.
4. Record the resulting full commit SHA here: `PENDING — no commit exists`.
5. Verify the commit contains the exact tested source and built artifact metadata.
6. With explicit authorization only, create the annotated tag `v1.0.0` on that commit.
7. With separate explicit authorization only, push the commit/tag and publish the GitHub release.

No tag, push, publication, or deployment was performed for this review.

## Draft GitHub Release notes

**Title:** ORVEXA v1.0.0

**Status:** Do not publish until the release gates above are complete.

**Summary**

ORVEXA provides document context, private document storage, extraction workflows, analysis, insights, tasks, goals, memory, search APIs, and a Flutter client.

**Planned highlights**

- FastAPI authentication and ownership-scoped APIs.
- Private document storage and extraction job lifecycle.
- PostgreSQL/pgvector migrations and search-supporting indexes.
- Flutter Web/mobile client with compile-time API configuration and secure token storage.
- Production configuration, deployment, backup, restore, and user documentation.

**Required before publication**

- Complete Flutter test/analyzer remediation.
- Complete real-account browser/device UAT and obtain QA/product sign-off.
- Bring the production-equivalent database to migration head after backup.
- Configure and verify the real AI provider.
- Complete vulnerability scanning, deployment health checks, and backup restore drill.

## Rollback instructions

1. Declare the incident, assign the rollback owner, and record the deployment and database versions.
2. Stop writes or place the backend in maintenance mode if data consistency is at risk.
3. If the application-only release is compatible with the existing schema, route traffic to the last known-good application image and frontend artifact.
4. If the schema or data must be recovered, restore a known-good PostgreSQL backup and matching document-storage backup into isolated resources first.
5. Never run `alembic downgrade` as a routine production rollback and never use `pg_restore --clean` against the original production database.
6. Validate storage keys, `/health`, `/ready`, authentication, representative document operations, logs, and error rates in isolation.
7. Obtain recovery approval, switch traffic through the HTTPS proxy, monitor, and retain the original resources until cleanup is approved.

Detailed recovery steps are in [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md).

## Final release recommendation

**Do not recommend v1.0.0 at this time.** Re-open this checklist after all unchecked release gates have objective evidence, all critical/high issues are resolved or formally accepted by the product owner, UAT is signed off, a release commit exists, and explicit authorization is provided for tagging and publication.
