from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.jwt import create_access_token
from app.database.base import Base
from app.database.models import Role, User
from app.database.session import get_db
from app.main import app
from app.modules.actions.models import Goal, Task
from app.modules.documents.document_models import Document
from app.modules.evidence import models as evidence_models  # noqa: F401
from app.modules.intelligence.context_models import UserContext
from app.modules.intelligence.models import AnalysisRun, IntelligenceInsight, IntelligenceRequest


@pytest_asyncio.fixture
async def search_api_client() -> AsyncIterator[dict[str, object]]:
	engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
	session_factory = async_sessionmaker(engine, expire_on_commit=False)
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)
	now = datetime.now(timezone.utc)
	user_a = User(id=uuid4(), email="search-a@example.com", password_hash="test", created_at=now, updated_at=now)
	user_b = User(id=uuid4(), email="search-b@example.com", password_hash="test", created_at=now, updated_at=now)
	role = Role(id=uuid4(), name="user")
	user_a.roles.append(role)
	user_b.roles.append(role)
	async with session_factory() as session:
		session.add_all([user_a, user_b])
		await session.flush()
		session.add_all([
			Document(user_id=user_a.id, original_filename="Roadmap.pdf", storage_key="roadmap-key", mime_type="application/pdf", file_size=10, sha256_hash="a" * 64, document_type="pdf", processing_status="ready", created_at=now, updated_at=now),
			Document(user_id=user_b.id, original_filename="Private.pdf", storage_key="private-key", mime_type="application/pdf", file_size=10, sha256_hash="b" * 64, document_type="pdf", processing_status="ready", created_at=now, updated_at=now),
			Task(user_id=user_a.id, title="Review roadmap", description="Review the project roadmap", status="pending", created_at=now, updated_at=now),
			Goal(user_id=user_a.id, title="Ship roadmap", description="Publish the roadmap", status="active", created_at=now, updated_at=now),
			UserContext(user_id=user_a.id, context_type="USER_PROVIDED_CONTEXT", title="Roadmap preference", category="project", content={"text": "Roadmap is quarterly"}, source_type="user", confirmation_status="confirmed", created_at=now, updated_at=now),
		])
		request = IntelligenceRequest(user_id=user_a.id, request_type="test", created_at=now, updated_at=now)
		session.add(request)
		await session.flush()
		run = AnalysisRun(user_id=user_a.id, request_id=request.id, status="completed", completed_at=now)
		session.add(run)
		await session.flush()
		session.add(IntelligenceInsight(user_id=user_a.id, analysis_run_id=run.id, title="Roadmap insight", description="A useful roadmap insight", category="finding", status="active", created_at=now))
		await session.commit()

	async def override_get_db() -> AsyncIterator[AsyncSession]:
		async with session_factory() as session:
			yield session

	app.dependency_overrides[get_db] = override_get_db
	try:
		async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
			yield {"client": client, "token_a": create_access_token(str(user_a.id), ["user"]), "token_b": create_access_token(str(user_b.id), ["user"])}
	finally:
		app.dependency_overrides.clear()
		await engine.dispose()


def auth(token: str) -> dict[str, str]:
	return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_global_search_returns_owned_groups_and_filters(search_api_client: dict[str, object]) -> None:
	client = search_api_client["client"]
	response = await client.get("/api/v1/search", headers=auth(search_api_client["token_a"]), params={"q": "roadmap", "category": "project"})
	assert response.status_code == 200
	body = response.json()
	assert {"documents", "tasks", "goals", "insights", "memories"} == set(body["groups"])
	assert [item["title"] for item in body["groups"]["memories"]["items"]] == ["Roadmap preference"]
	assert body["groups"]["tasks"]["total"] == 1
	assert body["groups"]["documents"]["total"] == 0


@pytest.mark.asyncio
async def test_global_search_enforces_ownership_and_pagination(search_api_client: dict[str, object]) -> None:
	client = search_api_client["client"]
	response = await client.get("/api/v1/search", headers=auth(search_api_client["token_b"]), params={"entities": "documents"})
	assert response.status_code == 200
	assert [item["title"] for item in response.json()["groups"]["documents"]["items"]] == ["Private.pdf"]

	page = await client.get("/api/v1/search", headers=auth(search_api_client["token_a"]), params={"entities": "tasks", "limit": 1, "offset": 1})
	assert page.status_code == 200
	assert page.json()["groups"]["tasks"] == {"items": [], "total": 1}


@pytest.mark.asyncio
async def test_global_search_validation_empty_results_and_authentication(search_api_client: dict[str, object]) -> None:
	client = search_api_client["client"]
	assert (await client.get("/api/v1/search")).status_code == 401
	assert (await client.get("/api/v1/search", headers=auth(search_api_client["token_a"]), params={"q": "x", "limit": 101})).status_code == 422
	assert (await client.get("/api/v1/search", headers=auth(search_api_client["token_a"]), params={"date_from": "2025-01-02T00:00:00Z", "date_to": "2025-01-01T00:00:00Z"})).status_code == 422
	empty = await client.get("/api/v1/search", headers=auth(search_api_client["token_a"]), params={"q": "does-not-exist"})
	assert empty.status_code == 200
	assert empty.json()["total"] == 0
