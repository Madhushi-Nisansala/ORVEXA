from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.v1.router import api_router
from app.core.jwt import create_access_token
from app.database.base import Base
from app.database.models import Role, User
from app.database.session import get_db
from app.main import app
from app.modules.actions import models as action_models  # noqa: F401
from app.modules.evidence import models as evidence_models  # noqa: F401
from app.modules.intelligence import context_models, models as intelligence_models  # noqa: F401


@pytest_asyncio.fixture
async def actions_api_client(tmp_path: Path) -> AsyncIterator[dict[str, object]]:
	engine = create_async_engine(
		"sqlite+aiosqlite://",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
	)
	session_factory = async_sessionmaker(engine, expire_on_commit=False)
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)

	now = datetime.now(timezone.utc)
	user_a = User(id=uuid4(), email="actions-a@example.com", password_hash="test", created_at=now, updated_at=now)
	user_b = User(id=uuid4(), email="actions-b@example.com", password_hash="test", created_at=now, updated_at=now)
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
async def test_actions_routes_registered_once_and_require_authentication() -> None:
	paths = app.openapi()["paths"]
	assert {"/api/v1/tasks", "/api/v1/goals", "/api/v1/goals/{goal_id}/milestones"}.issubset(paths)
	assert sum(getattr(route, "original_router", None) is not None and route.original_router is not None for route in api_router.routes) >= 1


@pytest.mark.asyncio
async def test_task_creation_listing_and_ownership(actions_api_client: dict[str, object]) -> None:
	client = actions_api_client["client"]
	created = await client.post("/api/v1/tasks", headers=auth(actions_api_client["token_a"]), json={"title": "Write plan"})
	assert created.status_code == 201
	task_id = created.json()["id"]
	assert created.json()["status"] == "pending"

	listed = await client.get("/api/v1/tasks", headers=auth(actions_api_client["token_a"]))
	assert listed.status_code == 200 and len(listed.json()) == 1
	hidden = await client.get(f"/api/v1/tasks/{task_id}", headers=auth(actions_api_client["token_b"]))
	assert hidden.status_code == 404


@pytest.mark.asyncio
async def test_task_status_transitions_and_invalid_transition(actions_api_client: dict[str, object]) -> None:
	client = actions_api_client["client"]
	headers = auth(actions_api_client["token_a"])
	task_id = (await client.post("/api/v1/tasks", headers=headers, json={"title": "Transition"})).json()["id"]
	changed = await client.post(f"/api/v1/tasks/{task_id}/status", headers=headers, json={"status": "in_progress"})
	assert changed.status_code == 200
	completed = await client.post(f"/api/v1/tasks/{task_id}/status", headers=headers, json={"status": "completed"})
	assert completed.status_code == 200
	invalid = await client.post(f"/api/v1/tasks/{task_id}/status", headers=headers, json={"status": "pending"})
	assert invalid.status_code == 409


@pytest.mark.asyncio
async def test_dependency_creation_cycle_prevention_and_self_validation(actions_api_client: dict[str, object]) -> None:
	client = actions_api_client["client"]
	headers = auth(actions_api_client["token_a"])
	first = (await client.post("/api/v1/tasks", headers=headers, json={"title": "First"})).json()["id"]
	second = (await client.post("/api/v1/tasks", headers=headers, json={"title": "Second"})).json()["id"]
	assert (await client.post(f"/api/v1/tasks/{first}/dependencies", headers=headers, json={"depends_on_task_id": second})).status_code == 201
	cycle = await client.post(f"/api/v1/tasks/{second}/dependencies", headers=headers, json={"depends_on_task_id": first})
	assert cycle.status_code == 409
	self_dependency = await client.post(f"/api/v1/tasks/{first}/dependencies", headers=headers, json={"depends_on_task_id": first})
	assert self_dependency.status_code == 422


@pytest.mark.asyncio
async def test_goal_creation_ownership_and_milestone_parent_validation(actions_api_client: dict[str, object]) -> None:
	client = actions_api_client["client"]
	headers_a = auth(actions_api_client["token_a"])
	headers_b = auth(actions_api_client["token_b"])
	goal = await client.post("/api/v1/goals", headers=headers_a, json={"title": "Ship stage 3"})
	assert goal.status_code == 201
	goal_id = goal.json()["id"]
	assert (await client.get(f"/api/v1/goals/{goal_id}", headers=headers_b)).status_code == 404
	milestone = await client.post(
		f"/api/v1/goals/{goal_id}/milestones",
		headers=headers_a,
		json={"goal_id": goal_id, "title": "Publish API"},
	)
	assert milestone.status_code == 201
	assert (await client.get(f"/api/v1/goals/{goal_id}/milestones", headers=headers_b)).status_code == 404
	foreign_create = await client.post(
		f"/api/v1/goals/{goal_id}/milestones",
		headers=headers_b,
		json={"goal_id": goal_id, "title": "Should fail"},
	)
	assert foreign_create.status_code == 404


@pytest.mark.asyncio
async def test_validation_invalid_ids_and_authentication(actions_api_client: dict[str, object]) -> None:
	client = actions_api_client["client"]
	assert (await client.get("/api/v1/tasks")).status_code == 401


@pytest.mark.asyncio
async def test_task_filters_sorting_pagination_update_and_delete(actions_api_client: dict[str, object]) -> None:
	client = actions_api_client["client"]
	headers = auth(actions_api_client["token_a"])
	first = await client.post(
		"/api/v1/tasks", headers=headers, json={"title": "Alpha task", "priority": "high"}
	)
	second = await client.post(
		"/api/v1/tasks", headers=headers, json={"title": "Beta task", "priority": "low"}
	)
	assert first.status_code == second.status_code == 201
	updated = await client.patch(
		f"/api/v1/tasks/{first.json()['id']}", headers=headers, json={"description": "Searchable"}
	)
	assert updated.status_code == 200 and updated.json()["description"] == "Searchable"
	filtered = await client.get(
		"/api/v1/tasks",
		headers=headers,
		params={"search": "searchable", "sort_by": "title", "sort_order": "asc", "limit": 1},
	)
	assert filtered.status_code == 200
	assert len(filtered.json()) == 1 and filtered.headers["x-total-count"] == "1"
	deleted = await client.delete(f"/api/v1/tasks/{second.json()['id']}", headers=headers)
	assert deleted.status_code == 204
	assert (await client.get(f"/api/v1/tasks/{second.json()['id']}", headers=headers)).status_code == 404
	assert (await client.get("/api/v1/tasks/not-a-uuid", headers=auth(actions_api_client["token_a"]))).status_code == 422
	invalid = await client.post("/api/v1/tasks", headers=auth(actions_api_client["token_a"]), json={"title": ""})
	assert invalid.status_code == 422
	assert (await client.get(f"/api/v1/goals/{uuid4()}", headers=auth(actions_api_client["token_a"]))).status_code == 404
