from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.database.session import SessionLocal, engine
from app.modules.documents.analysis_models import DocumentProcessingJob
from app.modules.documents.document_models import Document
from app.modules.documents.document_service import DocumentNotFoundError
from app.modules.documents.storage import LocalStorageProvider
from app.modules.extraction.extractors import CapabilityUnavailable, ExtractionError
from app.modules.extraction.service import ExtractionService

logger = logging.getLogger(__name__)

CLAIMABLE_STATUSES = ("queued", "retry_pending")
REQUIRED_SCHEMA_REVISION = "0006_stage2_extraction_jobs"
APPROVED_DATABASE_HOSTS = frozenset({"localhost", "127.0.0.1"})
APPROVED_DATABASE_PORTS = frozenset({5432})
APPROVED_DATABASE_NAMES = frozenset({"orvexa_db"})


class WorkerStartupError(RuntimeError):
	pass


def utc_now() -> datetime:
	return datetime.now(timezone.utc)


def retry_delay(attempt: int, settings: Settings) -> int:
	return min(
		settings.extraction_retry_max_delay_seconds,
		settings.extraction_retry_base_delay_seconds * (2 ** max(0, attempt - 1)),
	)


def _database_target(settings: Settings) -> tuple[str, int, str]:
	url = settings.get_database_url()
	parsed = urlparse(url)
	if parsed.scheme not in {"postgresql", "postgresql+asyncpg"}:
		raise WorkerStartupError("Worker requires a PostgreSQL database URL")
	try:
		host = (parsed.hostname or "").lower()
		port = parsed.port or 5432
	except ValueError as exc:
		raise WorkerStartupError("Worker database port is invalid") from exc
	database = parsed.path.lstrip("/")
	return host, port, database


def validate_worker_startup(settings: Settings) -> None:
	host, port, database = _database_target(settings)
	if database == "nova_health":
		raise WorkerStartupError("Worker must never use the nova_health database")
	if host not in APPROVED_DATABASE_HOSTS:
		raise WorkerStartupError("Worker database hostname is not approved")
	if port not in APPROVED_DATABASE_PORTS:
		raise WorkerStartupError("Worker database port is not approved")
	if database not in APPROVED_DATABASE_NAMES:
		raise WorkerStartupError("Worker database name is not approved")
	if settings.worker_schema_revision != REQUIRED_SCHEMA_REVISION:
		raise WorkerStartupError(
		f"Worker requires independently verified schema revision {REQUIRED_SCHEMA_REVISION}"
	)


def _safe_error_message(error: str, fallback: str) -> str:
	message = " ".join(error.split())[:500]
	return message or fallback


async def recover_stale_jobs(session: AsyncSession, settings: Settings) -> int:
	cutoff = utc_now() - timedelta(seconds=settings.worker_stale_timeout_seconds)
	result = await session.scalars(
		select(DocumentProcessingJob).where(
			DocumentProcessingJob.status == "processing",
			DocumentProcessingJob.claimed_at < cutoff,
		).with_for_update(skip_locked=True)
	)
	recovered = 0
	for job in result:
		job.claim_token = None
		job.claimed_at = None
		if job.attempts >= job.max_attempts:
			job.status = "failed"
			job.error_message = "Processing lease expired after the maximum attempts"
			job.completed_at = utc_now()
		else:
			job.status = "retry_pending"
			job.available_at = utc_now()
			job.error_message = "Processing lease expired; job requeued"
		recovered += 1
	if recovered:
		await session.commit()
		logger.warning("Recovered %d stale extraction jobs", recovered)
	return recovered


async def claim_job(session: AsyncSession) -> DocumentProcessingJob | None:
	now = utc_now()
	job = await session.scalar(
		select(DocumentProcessingJob)
		.where(
			DocumentProcessingJob.status.in_(CLAIMABLE_STATUSES),
			DocumentProcessingJob.available_at <= now,
		)
		.order_by(DocumentProcessingJob.available_at, DocumentProcessingJob.created_at)
		.with_for_update(skip_locked=True)
		.limit(1)
	)
	if job is None:
		return None
	job.status = "processing"
	job.attempts += 1
	job.started_at = now
	job.claimed_at = now
	job.claim_token = uuid4().hex
	await session.commit()
	logger.info("Claimed extraction job %s for document %s (attempt %d)", job.id, job.document_id, job.attempts)
	return job


async def _fail_job(
	session: AsyncSession,
	job: DocumentProcessingJob,
	claim_token: str,
	error: str,
	settings: Settings,
	retryable: bool,
) -> None:
	owned_job = await session.scalar(
		select(DocumentProcessingJob)
		.where(DocumentProcessingJob.id == job.id, DocumentProcessingJob.claim_token == claim_token)
		.with_for_update()
	)
	if owned_job is None:
		logger.warning("Skipped finalization for job %s because its claim is no longer owned", job.id)
		return
	owned_job.error_message = _safe_error_message(error, "Extraction failed")
	owned_job.claim_token = None
	owned_job.claimed_at = None
	if retryable and owned_job.attempts < owned_job.max_attempts:
		owned_job.status = "retry_pending"
		owned_job.available_at = utc_now() + timedelta(seconds=retry_delay(owned_job.attempts, settings))
		logger.warning("Extraction job %s scheduled for retry (attempt %d)", job.id, owned_job.attempts)
	else:
		owned_job.status = "failed"
		owned_job.completed_at = utc_now()
		document = await session.scalar(
			select(Document).where(Document.id == owned_job.document_id)
		)
		if document is not None:
			document.processing_status = "failed"
			document.extraction_status = "failed"
			document.updated_at = utc_now()
		logger.error("Extraction job %s failed permanently", job.id)
	await session.commit()


async def process_one(
	session_factory: async_sessionmaker[AsyncSession], settings: Settings | None = None
) -> bool:
	settings = settings or get_settings()
	async with session_factory() as session:
		await recover_stale_jobs(session, settings)
		job = await claim_job(session)
		if job is None:
			return False
		claim_token = job.claim_token
		assert claim_token is not None
		try:
			document = await session.scalar(
				select(Document).where(Document.id == job.document_id, Document.deleted_at.is_(None))
			)
			if document is None:
				raise DocumentNotFoundError("Source document is unavailable")
			extraction = await ExtractionService(
				session, LocalStorageProvider(settings.document_storage_root)
			).extract(document, job)
			if extraction.status == "failed":
				await _fail_job(session, job, claim_token, extraction.error_summary or "Extraction failed", settings, False)
			else:
				owned_job = await session.scalar(
					select(DocumentProcessingJob)
					.where(DocumentProcessingJob.id == job.id, DocumentProcessingJob.claim_token == claim_token)
					.with_for_update()
				)
				if owned_job is None:
					logger.warning("Skipped completion for job %s because its claim is no longer owned", job.id)
				else:
					owned_job.claim_token = None
					owned_job.claimed_at = None
					owned_job.status = "completed"
					owned_job.completed_at = extraction.completed_at or utc_now()
					owned_job.error_message = extraction.error_summary if extraction.status == "partial" else None
					await session.commit()
					logger.info("Completed extraction job %s with status %s", job.id, extraction.status)
		except CapabilityUnavailable as exc:
			await session.rollback()
			await _fail_job(session, job, claim_token, "Extraction capability unavailable", settings, False)
		except (DocumentNotFoundError, ExtractionError, OSError) as exc:
			await session.rollback()
			retryable = isinstance(exc, OSError) or "timed out" in str(exc).lower()
			await _fail_job(session, job, claim_token, str(exc), settings, retryable)
		except Exception as exc:
			await session.rollback()
			logger.error("Unexpected extraction worker failure for job %s (error_type=%s)", job.id, type(exc).__name__)
			await _fail_job(session, job, claim_token, "Unexpected extraction worker failure", settings, True)
	return True


async def run_worker(
	session_factory: async_sessionmaker[AsyncSession] = SessionLocal,
	settings: Settings | None = None,
	shutdown_event: asyncio.Event | None = None,
) -> None:
	settings = settings or get_settings()
	validate_worker_startup(settings)
	shutdown_event = shutdown_event or asyncio.Event()
	logger.info("Document extraction worker started")
	try:
		while not shutdown_event.is_set():
			try:
				processed = await process_one(session_factory, settings)
			except asyncio.CancelledError:
				raise
			except Exception as exc:
				logger.error("Worker iteration failed (error_type=%s)", type(exc).__name__)
				processed = False
				try:
					await asyncio.wait_for(shutdown_event.wait(), settings.worker_error_backoff_seconds)
				except asyncio.TimeoutError:
					pass
			if not processed and not shutdown_event.is_set():
				try:
					await asyncio.wait_for(shutdown_event.wait(), settings.worker_poll_interval_seconds)
				except asyncio.TimeoutError:
					pass
	except asyncio.CancelledError:
		logger.info("Document extraction worker shutting down")
		raise
	finally:
		logger.info("Document extraction worker stopped")


async def run() -> None:
	await run_worker()


if __name__ == "__main__":
	asyncio.run(run())
