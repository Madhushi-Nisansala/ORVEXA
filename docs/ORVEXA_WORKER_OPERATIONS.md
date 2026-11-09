# ORVEXA Document Worker Operations

## Current readiness

**WORKER NOT READY — DATABASE SCHEMA MIGRATION REQUIRED**

The configured PostgreSQL database was last independently verified at
`0005_document_extractions`. The worker requires migration
`0006_stage2_extraction_jobs`, which adds `max_attempts`, lease fields, and
claim indexes. Do not set `WORKER_SCHEMA_REVISION` or start the worker until an
explicitly approved migration process has applied 0006 and independently
verified the resulting revision.

The worker never runs migrations, resets data, or alters the schema during
startup.

## Architecture

The API and document worker are separate processes:

- **API process:** `app.main:app`, normally managed by Uvicorn. API startup
  does not import, create, or launch a document worker. Multiple Uvicorn
  workers therefore do not create duplicate document workers.
- **Worker process:** `app.workers.document_worker`, launched as a Python
  module. It claims queued extraction jobs using database row locks and
  `SKIP LOCKED`, then processes each claim independently.
- **Database:** shared PostgreSQL job state. A claim token identifies the
  worker that owns a processing lease. Completion and failure updates verify
  that token before changing the job.

The existing `/health` and `/ready` endpoints report API/database status only;
they do not claim that a separately managed worker is running. Worker process
liveness is checked through its process, PID file, and worker log.

## Startup prerequisites

1. Complete the approved database migration procedure through
   `0006_stage2_extraction_jobs`.
2. Independently verify the database revision and record the verification.
3. Configure the approved local development target only:
   - Host: `localhost` or `127.0.0.1`
   - Port: `5432`
   - Database: `orvexa_db`
   - `nova_health` is never an allowed worker database.
4. Set `WORKER_SCHEMA_REVISION=0006_stage2_extraction_jobs` only after step 2.
5. Set database credentials and storage/extractor configuration through the
   environment or the backend `.env` file. Credentials are not command-line
   arguments.
6. Install backend dependencies and run tests using an isolated SQLite or
   mocked database. Do not use the worker process as a migration check.

The Python worker performs the same immutable target and schema checks before
processing its first job. A rejected target or missing schema assertion stops
before job processing.

## API process

From the repository root, the documented direct development command is:

```powershell
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

The API may be started independently of the worker. API output should be
redirected to an API-specific log when running it outside the provided script.

## Worker process

Only after all startup prerequisites are met, run this from the repository
root:

```powershell
$env:WORKER_SCHEMA_REVISION = '0006_stage2_extraction_jobs'
python -m app.workers.document_worker
```

This command launches exactly one worker process. Do not put it in FastAPI
lifespan/startup hooks and do not run it once per Uvicorn worker.

The worker startup command does not run Alembic, connect to `nova_health`,
reset a schema, or automatically migrate the database.

## Windows PowerShell process management

The safe development launcher keeps API and worker logs and PID files
separate. It is not run by this implementation or by the test suite.

Start only the API:

```powershell
.\scripts\Manage-OrvexaProcesses.ps1 -StartApi
```

After schema migration and independent verification, set the schema assertion
and start only the worker:

```powershell
$env:WORKER_SCHEMA_REVISION = '0006_stage2_extraction_jobs'
.\scripts\Manage-OrvexaProcesses.ps1 -StartWorker
```

Start both as two separate processes only when the worker prerequisites are
met:

```powershell
$env:WORKER_SCHEMA_REVISION = '0006_stage2_extraction_jobs'
.\scripts\Manage-OrvexaProcesses.ps1 -StartApi -StartWorker
```

The launcher validates the database URL/host/port/name against its explicit
allowlist, rejects `nova_health`, and refuses worker startup unless the schema
revision assertion is present. It never runs migrations. Logs are written to
`logs/api.out.log`, `logs/api.err.log`, `logs/worker.out.log`, and
`logs/worker.err.log`; PID files are stored in `logs/api.pid` and
`logs/worker.pid`.

Stop managed processes:

```powershell
.\scripts\Manage-OrvexaProcesses.ps1 -Stop
```

For a directly launched process, send Ctrl+C to that process. The worker
handles cancellation, finishes its current cancellation boundary, logs
shutdown, and exits without starting another claim.

## Job claiming and recovery

- Claimable states are `queued` and `retry_pending` when `available_at` has
  elapsed.
- Claim selection uses `FOR UPDATE SKIP LOCKED`. The worker sets processing
  state, increments attempts, and records a random claim token in one
  transaction.
- A stale `processing` lease is recovered only under a row lock. Jobs below
  their maximum attempt count return to `retry_pending`; exhausted jobs become
  `failed`.
- A processing failure retries only while `attempts < max_attempts`.
  Backoff is exponential and capped by
  `EXTRACTION_RETRY_MAX_DELAY_SECONDS`; unexpected worker-loop errors also use
  a bounded error backoff so they cannot create a rapid infinite loop.
- Completion/failure verifies the claim token. If another worker has recovered
  a stale lease, the old process cannot overwrite the new owner’s state.
- Error logs contain job identifiers, status, attempt numbers, and exception
  types only. They do not log credentials, connection URLs, document text,
  or raw exception messages.

## Troubleshooting

### Worker refuses to start

Check `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB` or the host/port/database
in `DATABASE_URL`. Only the explicit local development target is approved.
Check that the database is not `nova_health`, and check that
`WORKER_SCHEMA_REVISION` is exactly `0006_stage2_extraction_jobs` after an
independent migration verification.

### Worker starts but no jobs are processed

Inspect `logs/worker.err.log` and `logs/worker.out.log`. Confirm that jobs are
in `queued` or `retry_pending`, that `available_at` has elapsed, and that the
source document has not been deleted. Do not bypass the claim token or remove
job locks manually.

### Jobs repeatedly retry

Inspect the sanitized failure status and extractor configuration. Retries are
bounded by each job's `max_attempts` and exponential delay. An exhausted job
is marked `failed`; repair the underlying issue before an explicitly approved
requeue operation.

### A worker process stops unexpectedly

The next worker can recover processing leases older than
`WORKER_STALE_TIMEOUT_SECONDS`. Confirm the old process is no longer running
before starting a replacement, then inspect stale-job recovery logs.

## Schema and recovery rules

Migration 0006 must be applied through the normal approved migration process,
not through this worker or its PowerShell launcher. Verify the Alembic revision
independently before enabling the schema environment variable. Preserve the
job table indexes and lease columns; do not reset the database to recover jobs.

If the database remains at revision 0005, leave the worker disabled:

**WORKER NOT READY — DATABASE SCHEMA MIGRATION REQUIRED**
