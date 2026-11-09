import asyncio
import concurrent.futures
import secrets
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from app.core.jwt import decode_access_token
from app.core.security import hash_refresh_token, utc_now
from app.database.models import RefreshToken, User, user_roles
from app.database.session import SessionLocal
from app.main import app

email = f"phase2.audit.{secrets.token_hex(8)}@example.com"
password = "AuditPassword!2026"
client = TestClient(app)
uid = None

def ok(value, message):
	if not value:
		raise AssertionError(message)
	print("PASS: " + message)

async def row(raw=None):
	async with SessionLocal() as db:
		user = await db.scalar(select(User).where(User.email == email))
		token = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw))) if raw else None
		return user, token

try:
	r = client.post('/api/v1/auth/register', json={'email': email, 'password': password, 'full_name': 'Phase 2 Audit'})
	ok(r.status_code == 201, 'real PostgreSQL registration succeeds')
	ok('password_hash' not in r.text and password not in r.text, 'registration response excludes password data')
	r = client.post('/api/v1/auth/register', json={'email': email, 'password': password})
	ok(r.status_code == 409, 'duplicate registration is rejected')
	r = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
	ok(r.status_code == 200, 'real PostgreSQL login succeeds')
	first = r.json(); access = first['access_token']; old = first['refresh_token']
	payload = decode_access_token(access)
	ok(payload['type'] == 'access' and payload['sub'], 'JWT has validated access type and subject')
	user, token = asyncio.run(row(old)); uid = user.id
	ok(user.password_hash.startswith('$argon2id$'), 'database password hash is Argon2id')
	ok(user.password_hash != password, 'database does not store plaintext password')
	ok(token.token_hash != old, 'database stores only refresh-token hash')
	ok(any(role.name == 'user' for role in user.roles), 'database assigns default user role')
	r = client.post('/api/v1/auth/login', json={'email': email, 'password': 'WrongPassword!2026'})
	ok(r.status_code == 401, 'invalid credentials are rejected')
	r = client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer ' + access})
	ok(r.status_code == 200, 'valid JWT reaches protected endpoint')
	r = client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer ' + access[:-1] + 'x'})
	ok(r.status_code == 401, 'tampered JWT is rejected')
	r = client.post('/api/v1/auth/refresh', json={'refresh_token': old})
	ok(r.status_code == 200, 'refresh succeeds')
	new = r.json()['refresh_token']; ok(new != old, 'refresh returns a new token')
	_, old_row = asyncio.run(row(old)); _, new_row = asyncio.run(row(new))
	ok(old_row.revoked_at is not None and old_row.replaced_by_token_id == new_row.id, 'old token is revoked and replacement linked')
	r = client.post('/api/v1/auth/refresh', json={'refresh_token': old})
	ok(r.status_code == 401, 'old token reuse is rejected')
	r = client.post('/api/v1/auth/refresh', json={'refresh_token': new})
	ok(r.status_code == 401, 'token family is revoked after reuse')
	expired_raw = secrets.token_urlsafe(64)
	async def add_expired():
		async with SessionLocal() as db:
			db.add(RefreshToken(user_id=uid, token_hash=hash_refresh_token(expired_raw), expires_at=utc_now() - timedelta(minutes=1), created_at=utc_now()))
			await db.commit()
	asyncio.run(add_expired())
	r = client.post('/api/v1/auth/refresh', json={'refresh_token': expired_raw})
	ok(r.status_code == 401, 'expired refresh token is rejected')
	r = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
	concurrent_raw = r.json()['refresh_token']
	def refresh_once():
		return TestClient(app).post('/api/v1/auth/refresh', json={'refresh_token': concurrent_raw}).status_code
	with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
		statuses = sorted(pool.map(lambda _: refresh_once(), range(2)))
	ok(statuses == [200, 401], f'concurrent refresh results are one success and one rejection: {statuses}')
finally:
	if uid:
		async def cleanup():
			async with SessionLocal() as db:
				await db.execute(delete(RefreshToken).where(RefreshToken.user_id == uid))
				await db.execute(delete(user_roles).where(user_roles.c.user_id == uid))
				await db.execute(delete(User).where(User.id == uid))
				await db.commit()
		asyncio.run(cleanup())
		print('PASS: targeted PostgreSQL audit cleanup completed')
