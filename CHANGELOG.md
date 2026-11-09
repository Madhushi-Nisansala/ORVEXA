# Changelog

All notable changes to ORVEXA are documented here. This project has no published release tag in the current repository state.

## [Unreleased]

### Added

- Release readiness checklist with verification evidence, release gates, rollback instructions, intended tag procedure, and draft GitHub release notes.
- Current user guide covering account access, documents, analysis, tasks, goals, memory, search, privacy, troubleshooting, and known limitations.
- README release-status and operations documentation links.

### Documented

- Final verification evidence: backend automated tests passed with required audit configuration, while Flutter tests/analyzer, migration state, real AI configuration, and production controls remain unresolved.
- UAT evidence: interactive browser/device and real-account acceptance was unavailable; UAT is not signed off.
- Production configuration, backup/restore expectations, and the restriction against committing secrets or operational artifacts.

### Known issues and release blockers

- The reviewed Flutter suite reported 10 failures, including authentication and document/dashboard navigation timeouts.
- Flutter analysis reported 19 issues, including protected/test-only Riverpod member access and deprecated APIs.
- The target database was behind Alembic head `0011_global_search_indexes`; no production migration was run during verification.
- No real AI provider credentials/model were configured or verified.
- The reviewed environment contained a local plaintext database credential and `DEBUG=true`; local environment files must never be used as production secret sources.
- Real browser/device UAT, production health checks, vulnerability scanning, and backup/recovery drill remain unverified.
- Dashboard context count and client-side aggregation, missing confirmed global Search UI, and “Coming soon” sections require product/engineering disposition.

## [1.0.0] — Not released

This version is reserved for the first official release. It must not be tagged or published until the release checklist is complete, all critical/high issues are resolved or formally accepted, UAT and production health are signed off, backup recovery is proven, and an approved release commit exists.

