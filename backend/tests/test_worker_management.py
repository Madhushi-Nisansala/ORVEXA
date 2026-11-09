import asyncio
from pathlib import Path

import pytest

from app.core.config import Settings
from app.workers import document_worker


def worker_settings(**overrides) -> Settings:
	values = {
		"database_url": "postgresql+asyncpg://user:password@localhost:5432/orvexa_db",
		"worker_schema_revision": document_worker.REQUIRED_SCHEMA_REVISION,
	}
	values.update(overrides)
	return Settings(**values)


def test_worker_rejects_unapproved_database_target() -> None:
	settings = worker_settings(database_url="postgresql+asyncpg://user:password@approved.example:5432/orvexa_db")

	with pytest.raises(document_worker.WorkerStartupError, match="hostname"):
		document_worker.validate_worker_startup(settings)


def test_worker_rejects_nova_health() -> None:
	settings = worker_settings(database_url="postgresql+asyncpg://user:password@localhost:5432/nova_health")

	with pytest.raises(document_worker.WorkerStartupError, match="nova_health"):
		document_worker.validate_worker_startup(settings)


def test_worker_requires_independently_verified_schema_revision() -> None:
	settings = worker_settings(worker_schema_revision="0005_document_extractions")

	with pytest.raises(document_worker.WorkerStartupError, match="0006_stage2_extraction_jobs"):
		document_worker.validate_worker_startup(settings)


def test_retry_delay_is_bounded() -> None:
	settings = worker_settings(
		extraction_retry_base_delay_seconds=30,
		extraction_retry_max_delay_seconds=60,
	)

	assert document_worker.retry_delay(1, settings) == 30
	assert document_worker.retry_delay(2, settings) == 60
	assert document_worker.retry_delay(20, settings) == 60


@pytest.mark.asyncio
async def test_worker_stops_gracefully_when_shutdown_event_is_set(monkeypatch) -> None:
	shutdown = asyncio.Event()
	calls = 0

	async def process_once(*args, **kwargs):
		nonlocal calls
		calls += 1
		shutdown.set()
		return False

	monkeypatch.setattr(document_worker, "process_one", process_once)
	await document_worker.run_worker(settings=worker_settings(), shutdown_event=shutdown)

	assert calls == 1


@pytest.mark.asyncio
async def test_worker_cancellation_is_propagated(monkeypatch) -> None:
	started = asyncio.Event()

	async def process_forever(*args, **kwargs):
		started.set()
		await asyncio.Event().wait()

	monkeypatch.setattr(document_worker, "process_one", process_forever)
	task = asyncio.create_task(document_worker.run_worker(settings=worker_settings()))
	await asyncio.wait_for(started.wait(), timeout=1)
	task.cancel()

	with pytest.raises(asyncio.CancelledError):
		await task


@pytest.mark.asyncio
async def test_worker_iteration_exception_does_not_kill_loop(monkeypatch, caplog) -> None:
	shutdown = asyncio.Event()
	calls = 0

	async def process_once(*args, **kwargs):
		nonlocal calls
		calls += 1
		if calls == 1:
			raise RuntimeError("document secret should not be logged")
		shutdown.set()
		return False

	monkeypatch.setattr(document_worker, "process_one", process_once)
	settings = worker_settings(worker_error_backoff_seconds=0.01, worker_poll_interval_seconds=0.01)
	caplog.set_level("ERROR", logger="app.workers.document_worker")
	await document_worker.run_worker(settings=settings, shutdown_event=shutdown)

	assert calls == 2
	assert "document secret should not be logged" not in caplog.text


def test_api_does_not_create_worker() -> None:
	main_source = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")

	assert "run_worker" not in main_source
	assert "document_worker" not in main_source
