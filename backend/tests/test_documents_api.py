from collections.abc import AsyncIterator
from datetime import datetime, timezone
import io
from pathlib import Path
from uuid import UUID, uuid4
import zipfile

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.jwt import create_access_token
from app.database.base import Base
from app.database.models import Role, User
from app.database.session import get_db
from app.main import app
from app.modules.documents.analysis_models import DocumentProcessingJob
from app.modules.documents.document_models import Document, DocumentPage
from app.modules.extraction.models import DocumentExtraction


@pytest_asyncio.fixture
async def document_api_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[dict[str, object]]:
	engine = create_async_engine(
		"sqlite+aiosqlite://",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
	)
	session_factory = async_sessionmaker(engine, expire_on_commit=False)
	settings = get_settings()
	old_root = settings.document_storage_root
	old_limit = settings.document_max_file_size_bytes
	settings.document_storage_root = str(tmp_path / "documents")
	settings.document_max_file_size_bytes = 1024

	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)

	now = datetime.now(timezone.utc)
	user_a = User(
		id=uuid4(), email="a@example.com", password_hash="test", created_at=now, updated_at=now
	)
	user_b = User(
		id=uuid4(), email="b@example.com", password_hash="test", created_at=now, updated_at=now
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
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		yield {
			"client": client,
			"user_a": user_a,
			"user_b": user_b,
			"token_a": create_access_token(str(user_a.id), ["user"]),
			"token_b": create_access_token(str(user_b.id), ["user"]),
		}
	app.dependency_overrides.clear()
	settings.document_storage_root = old_root
	settings.document_max_file_size_bytes = old_limit
	await engine.dispose()


def auth(token: str) -> dict[str, str]:
	return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_document_api_rejects_unauthenticated_upload(document_api_client: dict[str, object]) -> None:
	client = document_api_client["client"]
	response = await client.post(
		"/api/v1/documents", files={"file": ("note.txt", b"hello", "text/plain")}
	)
	assert response.status_code == 401


@pytest.mark.asyncio
async def test_document_api_rejects_missing_access_token(document_api_client: dict[str, object]) -> None:
	client = document_api_client["client"]
	response = await client.get("/api/v1/documents")
	assert response.status_code == 401


@pytest.mark.asyncio
async def test_document_api_rejects_invalid_access_token(document_api_client: dict[str, object]) -> None:
	client = document_api_client["client"]
	response = await client.get("/api/v1/documents", headers=auth("invalid-token"))
	assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
	("filename", "media_type", "content", "status_code"),
	[
		("note.exe", "application/octet-stream", b"MZ", 422),
		("note.txt", "application/pdf", b"hello", 422),
		("report.pdf", "application/pdf", b"not a pdf", 422),
		("empty.txt", "text/plain", b"", 422),
		("folder%2Fnote.txt", "text/plain", b"hello", 422),
		("note.txt", "text/plain", b"1" * 1025, 413),
	],
)
async def test_document_api_rejects_invalid_uploads(
	document_api_client: dict[str, object],
	filename: str,
	media_type: str,
	content: bytes,
	status_code: int,
) -> None:
	client = document_api_client["client"]
	token = document_api_client["token_a"]
	response = await client.post(
		"/api/v1/documents",
		files={"file": (filename, content, media_type)},
		headers=auth(token),
	)
	assert response.status_code == status_code
	assert "traceback" not in response.text.lower()


@pytest.mark.asyncio
async def test_document_api_returns_metadata_and_allows_owner_access(
	document_api_client: dict[str, object],
) -> None:
	client = document_api_client["client"]
	token = document_api_client["token_a"]
	content = b"%PDF-1.7\nORVEXA"
	response = await client.post(
		"/api/v1/documents",
		files={"file": ("report.pdf", content, "application/pdf")},
		headers=auth(token),
	)
	assert response.status_code == 201
	document = response.json()
	document_id = UUID(document["id"])
	assert document["original_filename"] == "report.pdf"
	assert document["mime_type"] == "application/pdf"
	assert document["file_size"] == len(content)
	assert document["document_type"] == "pdf"
	assert len(document["sha256_hash"]) == 64

	listed = await client.get("/api/v1/documents", headers=auth(token))
	fetched = await client.get(f"/api/v1/documents/{document_id}", headers=auth(token))
	downloaded = await client.get(f"/api/v1/documents/{document_id}/content", headers=auth(token))
	assert listed.status_code == 200 and listed.json()["total"] == 1
	assert fetched.status_code == 200 and fetched.json()["id"] == str(document_id)
	assert downloaded.status_code == 200
	assert downloaded.content == content
	assert downloaded.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
@pytest.mark.parametrize(
	("filename", "media_type", "content"),
	[
		("note.txt", "text/plain", b"plain text"),
		("data.csv", "text/csv", b"a,b\n1,2\n"),
		("image.png", "image/png", b"\x89PNG\r\n\x1a\n"),
		("image.jpg", "image/jpeg", b"\xff\xd8\xff"),
	],
)
async def test_document_api_accepts_supported_file_formats(
	document_api_client: dict[str, object],
	filename: str,
	media_type: str,
	content: bytes,
) -> None:
	client = document_api_client["client"]
	response = await client.post(
		"/api/v1/documents",
		files={"file": (filename, content, media_type)},
		headers=auth(document_api_client["token_a"]),
	)
	assert response.status_code == 201


@pytest.mark.asyncio
async def test_document_api_accepts_valid_docx_and_rejects_duplicate(
	document_api_client: dict[str, object],
) -> None:
	content_buffer = io.BytesIO()
	with zipfile.ZipFile(content_buffer, "w") as archive:
		archive.writestr("[Content_Types].xml", "<Types/>")
		archive.writestr("word/document.xml", "<document/>")
	content = content_buffer.getvalue()
	client = document_api_client["client"]
	headers = auth(document_api_client["token_a"])
	first = await client.post(
		"/api/v1/documents",
		files={"file": ("report.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
		headers=headers,
	)
	second = await client.post(
		"/api/v1/documents",
		files={"file": ("copy.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
		headers=headers,
	)
	assert first.status_code == 201
	assert second.status_code == 409


@pytest.mark.asyncio
async def test_document_api_owner_can_archive_and_delete(
	document_api_client: dict[str, object],
) -> None:
	client = document_api_client["client"]
	headers = auth(document_api_client["token_a"])
	upload = await client.post(
		"/api/v1/documents",
		files={"file": ("lifecycle.txt", b"lifecycle", "text/plain")},
		headers=headers,
	)
	document_id = upload.json()["id"]

	archived = await client.post(f"/api/v1/documents/{document_id}/archive", headers=headers)
	assert archived.status_code == 200
	assert archived.json()["archived_at"] is not None
	deleted = await client.delete(f"/api/v1/documents/{document_id}", headers=headers)
	assert deleted.status_code == 204
	assert (await client.get(f"/api/v1/documents/{document_id}", headers=headers)).status_code == 404


@pytest.mark.asyncio
async def test_document_api_enforces_cross_user_ownership_for_all_operations(
	document_api_client: dict[str, object],
) -> None:
	client = document_api_client["client"]
	token_a = document_api_client["token_a"]
	token_b = document_api_client["token_b"]
	upload = await client.post(
		"/api/v1/documents",
		files={"file": ("private.txt", b"private", "text/plain")},
		headers=auth(token_a),
	)
	document_id = upload.json()["id"]

	assert (await client.get("/api/v1/documents", headers=auth(token_b))).json()["total"] == 0
	for method, path in [
		("get", f"/api/v1/documents/{document_id}"),
		("get", f"/api/v1/documents/{document_id}/content"),
		("post", f"/api/v1/documents/{document_id}/extract"),
		("post", f"/api/v1/documents/{document_id}/retry"),
		("post", f"/api/v1/documents/{document_id}/archive"),
		("delete", f"/api/v1/documents/{document_id}"),
	]:
		response = await getattr(client, method)(path, headers=auth(token_b))
		assert response.status_code == 404

	assert (await client.get(f"/api/v1/documents/{document_id}", headers=auth(token_a))).status_code == 200


@pytest.mark.asyncio
async def test_document_api_does_not_expose_storage_key(document_api_client: dict[str, object]) -> None:
	client = document_api_client["client"]
	response = await client.post(
		"/api/v1/documents",
		files={"file": ("private.txt", b"private", "text/plain")},
		headers=auth(document_api_client["token_a"]),
	)
	assert response.status_code == 201
	assert "storage_key" not in response.json()


@pytest.mark.asyncio
async def test_analysis_api_requires_authentication_and_completed_extraction(
	document_api_client: dict[str, object],
) -> None:
	client = document_api_client["client"]
	unauthenticated = await client.post(f"/api/v1/documents/{uuid4()}/analyze")
	assert unauthenticated.status_code == 401
	upload = await client.post(
		"/api/v1/documents",
		files={"file": ("analysis.txt", b"source content", "text/plain")},
		headers=auth(document_api_client["token_a"]),
	)
	analysis = await client.post(
		f"/api/v1/documents/{upload.json()['id']}/analyze",
		headers=auth(document_api_client["token_a"]),
	)
	assert analysis.status_code == 409
	assert "completed document extraction" in analysis.json()["detail"]


@pytest.mark.asyncio
async def test_analysis_api_preserves_document_ownership(
	document_api_client: dict[str, object],
) -> None:
	client = document_api_client["client"]
	upload = await client.post(
		"/api/v1/documents",
		files={"file": ("private.txt", b"private source", "text/plain")},
		headers=auth(document_api_client["token_a"]),
	)
	response = await client.post(
		f"/api/v1/documents/{upload.json()['id']}/analyze",
		headers=auth(document_api_client["token_b"]),
	)
	assert response.status_code == 404