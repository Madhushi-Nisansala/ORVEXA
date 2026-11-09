# ORVEXA Backup and Restore

Backups are an operational requirement and are not created automatically by this repository. Configure provider-managed PostgreSQL backups and a separate encrypted backup process for document storage before production use.

## Recovery objectives

Record these values in the production change record:

- **RPO**: maximum acceptable data loss, for example 24 hours for scheduled backups or a provider-defined point-in-time window.
- **RTO**: maximum acceptable recovery time, for example 4 hours.
- Backup retention period and geographic/encryption requirements.
- Named backup owner and restore approver.

Never test restore commands against the production database or production storage path. Restore into an isolated resource first.

## What must be backed up

1. PostgreSQL schema and data, including extensions and indexes.
2. Private document files under `DOCUMENT_STORAGE_ROOT`.
3. Storage metadata already recorded in PostgreSQL, including document storage keys.
4. Deployment configuration templates and migration history, but never populated secrets.
5. Any provider-specific encryption key metadata required to decrypt backups, stored separately under the organization's key-management policy.

A database-only backup is incomplete because document metadata can refer to files stored outside PostgreSQL.

## PostgreSQL backup

Prefer the managed database provider's encrypted automated backups and point-in-time recovery. Confirm that backups include the `pgvector` extension state, are retained for the agreed period, and can be restored to a new private instance.

For a self-managed PostgreSQL service, create a compressed logical backup from a trusted host. Supply the password through the process environment or a secret manager, not in shell history:

```powershell
$env:PGPASSWORD = '<injected-at-runtime>'
pg_dump --format=custom --no-owner --no-acl --host=<db-host> --port=5432 --username=<db-user> --dbname=<db-name> --file=orvexa-<timestamp>.dump
Remove-Item Env:PGPASSWORD
```

Store the dump in encrypted, access-controlled backup storage. Verify the file checksum and upload status. Do not put the dump in the repository or a public bucket.

For a physical/self-managed backup, use the PostgreSQL provider's documented base-backup and WAL archiving process instead of mixing it with `pg_dump` instructions.

## Document storage backup

The current production Compose file mounts the named volume `document-storage` at `/app/storage/documents`. Prefer a provider snapshot or an encrypted file-level backup that preserves paths and permissions.

Example file-level pattern from a host with the volume mounted at `<storage-mount>`:

```powershell
tar -C <storage-mount> -czf orvexa-documents-<timestamp>.tar.gz .
```

Encrypt the archive before transferring it to backup storage, restrict access, record its checksum, and apply retention/lifecycle rules. The archive must not be publicly readable.

If an S3-compatible provider is implemented later, enable versioning, server-side encryption, restricted IAM access, lifecycle retention, and a documented bucket restore procedure. Do not assume the current `LocalStorageProvider` can read an object-storage bucket without an application change.

## Backup schedule and verification

A reasonable starting schedule is:

- Managed PostgreSQL point-in-time recovery or daily full backup.
- Daily document backup, with more frequent synchronization if the RPO requires it.
- Monthly restore drill in an isolated environment.
- Alert when any scheduled backup is missing, too small, corrupt, or outside the retention policy.

A successful backup job is not proof of recoverability. Periodically restore both database and documents, run migrations only when appropriate for the restored version, and verify that representative document records resolve to the restored storage keys.

## Restore procedure

1. Declare the incident, record the target recovery timestamp, and stop writes or place the backend in maintenance mode.
2. Create new isolated PostgreSQL and storage resources. Do not delete the original resources.
3. Restore the PostgreSQL backup using the provider workflow or:

   ```powershell
   $env:PGPASSWORD = '<injected-at-runtime>'
   createdb --host=<new-db-host> --port=5432 --username=<db-user> <new-db-name>
   pg_restore --clean --if-exists --no-owner --no-acl --host=<new-db-host> --port=5432 --username=<db-user> --dbname=<new-db-name> orvexa-<timestamp>.dump
   Remove-Item Env:PGPASSWORD
   ```

   Use `--clean` only on the newly created restore database. Never run it against the original production database.
4. Restore the document archive or volume snapshot to the new storage path/bucket.
5. Confirm that database storage keys and restored files match. Check file counts, checksums where available, and representative downloads.
6. Configure a temporary backend instance against the restored resources. Run `alembic current`, then use `alembic upgrade head` only if the restored schema intentionally needs to move forward.
7. Verify `/health`, `/ready`, authentication, document listing, upload, download, and deletion behavior in the isolated environment.
8. Obtain recovery approval, update the backend secret configuration to the restored database/storage resources, and switch traffic through the HTTPS proxy.
9. Monitor errors, readiness, logs, and storage access. Keep the original resources untouched until the incident owner approves cleanup.

## Migration safety during recovery

Inspect migration history before applying migrations. Take a fresh backup before any forward migration. Do not downgrade production as a routine rollback; restore a known-good database backup only under an approved recovery plan, because application and schema versions may not be backward-compatible.

## Restore acceptance checklist

- [ ] Correct recovery timestamp and backup versions recorded.
- [ ] PostgreSQL restore completed in an isolated resource.
- [ ] Document storage restored and protected from public access.
- [ ] Database storage keys resolve to restored documents.
- [ ] `alembic current` is recorded and schema compatibility is confirmed.
- [ ] `/health` and `/ready` return HTTP 200 in the isolated deployment.
- [ ] Representative authenticated document operations succeed.
- [ ] Secrets were injected through the secret manager and not committed or logged.
- [ ] Original production data was not deleted or overwritten.
- [ ] Recovery owner approved traffic restoration.
