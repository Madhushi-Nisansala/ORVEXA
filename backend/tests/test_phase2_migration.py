import asyncio
import uuid

import asyncpg
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings


@pytest.mark.asyncio
async def test_phase2_migration_seeded_roles_are_postgresql_uuids() -> None:
	settings = get_settings()
	engine = create_async_engine(
		settings.get_database_url(),
		pool_pre_ping=True,
		connect_args={"timeout": settings.database_connect_timeout},
	)

	try:
		try:
			async with asyncio.timeout(settings.database_connect_timeout):
				connection = await engine.connect()
		except (asyncpg.PostgresConnectionError, DBAPIError, OSError, TimeoutError) as exc:
			pytest.skip(f"PostgreSQL is unavailable: {type(exc).__name__}")

		try:
			try:
				revision = await connection.scalar(text("SELECT version_num FROM alembic_version"))
				rows = (
					await connection.execute(
						text(
							"""
							SELECT id, name, pg_typeof(id)::text AS id_type
							FROM roles
							WHERE name IN ('user', 'admin')
							ORDER BY name
							"""
						)
					)
				).mappings().all()
			except DBAPIError as exc:
				pytest.skip(f"PostgreSQL schema is unavailable: {type(exc).__name__}")
		finally:
			await connection.close()

		assert revision in {
			"0002_phase3_documents",
			"0003_stage1b_domain_foundation",
			"0004_document_lifecycle",
			"0005_document_extractions",
			"0006_stage2_extraction_jobs",
			"0007_stage3_document_analysis",
			"0008_stage4_context_privacy",
			"0009_document_insights",
		}
		assert rows == [
			{
				"id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
				"name": "admin",
				"id_type": "uuid",
			},
			{
				"id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
				"name": "user",
				"id_type": "uuid",
			},
		]
	finally:
		await engine.dispose()
