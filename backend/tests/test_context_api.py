from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.jwt import create_access_token
from app.api.v1.endpoints.context import router as context_router
from app.api.v1.router import api_router
from app.database.base import Base
from app.database.models import Role, User
from app.database.session import get_db
from app.main import app
from app.modules.evidence import models as evidence_models  # noqa: F401
from app.modules.intelligence import context_models, models as intelligence_models  # noqa: F401


@pytest_asyncio.fixture
async def context_api_client(tmp_path: Path) -> AsyncIterator[dict[str, object]]:
	engine = create_async_engine(
		"sqlite+aiosqlite://",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
	)
	session_factory = async_sessionmaker(engine, expire_on_commit=False)

	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)

	now = datetime.now(timezone.utc)
	user_a = User(
		id=uuid4(),
		email="context-a@example.com",
		password_hash="test",
		created_at=now,
		updated_at=now,
	)
	user_b = User(
		id=uuid4(),
		email="context-b@example.com",
		password_hash="test",
		created_at=now,
		updated_at=now,
	)
	role = Role(id=uuid4(), name="user")
	user_a.roles.append(role)
	user_b.roles.append(role)

	async with session_factory() as session:
		session.add_all([user_a, user_b])
		await session.commit()

	async def override_get_db() -> AsyncIterator[AsyncSession]:
		async with session_factory() as session:
			yield session

	app.dependency_overrides[get_db] = override_get_db
	transport = httpx.ASGITransport(app=app)
	try:
		async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
			yield {
				"client": client,
				"user_a": user_a,
				"user_b": user_b,
				"token_a": create_access_token(str(user_a.id), ["user"]),
				"token_b": create_access_token(str(user_b.id), ["user"]),
			}
	finally:
		app.dependency_overrides.clear()
		await engine.dispose()


def auth(token: str) -> dict[str, str]:
	return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_context_routes_are_registered_once_under_api_prefix() -> None:
	paths = app.openapi()["paths"]
	context_registrations = [
		route
		for route in api_router.routes
		if getattr(route, "original_router", None) is context_router
	]

	assert len(context_registrations) == 1
	assert {
		"/api/v1/context",
		"/api/v1/context/{context_id}",
		"/api/v1/context/{context_id}/confirm",
		"/api/v1/context/{context_id}/reject",
		"/api/v1/context/preferences",
		"/api/v1/context/relevant",
		"/api/v1/insights",
	}.issubset(paths)


@pytest.mark.asyncio
async def test_context_routes_require_authentication(context_api_client: dict[str, object]) -> None:
	client = context_api_client["client"]

	response = await client.get("/api/v1/context")

	assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_users_can_create_retrieve_and_only_access_owned_context(
	context_api_client: dict[str, object],
) -> None:
	client = context_api_client["client"]
	token_a = context_api_client["token_a"]
	token_b = context_api_client["token_b"]

	created = await client.post(
		"/api/v1/context",
		headers=auth(token_a),
		json={
			"category": "preferences",
			"content": {"language": "en"},
		},
	)

	assert created.status_code == 201
	context_id = UUID(created.json()["id"])
	assert created.json()["context_type"] == "USER_PROVIDED_CONTEXT"
	assert created.json()["confirmation_status"] == "confirmed"

	retrieved = await client.get(f"/api/v1/context/{context_id}", headers=auth(token_a))
	assert retrieved.status_code == 200
	assert retrieved.json()["content"] == {"language": "en"}

	other_user = await client.get(f"/api/v1/context/{context_id}", headers=auth(token_b))
	assert other_user.status_code == 404
	assert other_user.json()["detail"] == "Context not found"

	other_user_list = await client.get("/api/v1/context", headers=auth(token_b))
	assert other_user_list.status_code == 200
	assert other_user_list.json() == []


@pytest.mark.asyncio
async def test_context_validation_errors_remain_unchanged(
	context_api_client: dict[str, object],
) -> None:
	client = context_api_client["client"]
	token = context_api_client["token_a"]

	invalid_payload = await client.post(
		"/api/v1/context",
		headers=auth(token),
		json={"category": "", "content": {"value": "x"}},
	)
	assert invalid_payload.status_code == 422

	invalid_evidence_context = await client.post(
		"/api/v1/context",
		headers=auth(token),
		json={
			"context_type": "USER_PROVIDED_CONTEXT",
			"category": "preferences",
			"content": {"language": "en"},
			"evidence_reference": str(uuid4()),
		},
	)
	assert invalid_evidence_context.status_code == 422
	assert invalid_evidence_context.json()["detail"] == (
		"Evidence-linked context must be document-derived or confirmed"
	)


@pytest.mark.asyncio
async def test_memory_lifecycle_search_archive_and_permanent_delete(
	context_api_client: dict[str, object],
) -> None:
	client = context_api_client["client"]
	token_a = context_api_client["token_a"]
	token_b = context_api_client["token_b"]

	created = await client.post(
		"/api/v1/memory",
		headers=auth(token_a),
		json={"title": "Launch decision", "category": "decisions", "content": {"text": "Launch in June"}},
	)
	assert created.status_code == 201
	assert created.json()["title"] == "Launch decision"
	memory_id = created.json()["id"]

	search = await client.get("/api/v1/memory", headers=auth(token_a), params={"search": "June", "category": "decisions"})
	assert search.status_code == 200
	assert [item["id"] for item in search.json()] == [memory_id]

	other_user = await client.get(f"/api/v1/memory/{memory_id}", headers=auth(token_b))
	assert other_user.status_code == 404

	archived = await client.post(f"/api/v1/memory/{memory_id}/archive", headers=auth(token_a))
	assert archived.status_code == 200
	assert archived.json()["is_active"] is False
	assert (await client.get("/api/v1/memory", headers=auth(token_a))).json() == []

	deleted = await client.delete(f"/api/v1/memory/{memory_id}/permanent", headers=auth(token_a))
	assert deleted.status_code == 204
	assert (await client.get(f"/api/v1/memory/{memory_id}", headers=auth(token_a))).status_code == 404
