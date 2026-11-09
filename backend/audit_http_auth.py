import concurrent.futures
import secrets
import httpx

base = 'http://127.0.0.1:8766'
email = f'phase2.audit.{secrets.token_hex(8)}@example.com'
password = 'AuditPassword!2026'
def post(path, **kwargs):
	return httpx.post(base + path, timeout=10, **kwargs)
registration = post('/api/v1/auth/register', json={'email': email, 'password': password, 'full_name': 'Phase 2 Audit'})
duplicate = post('/api/v1/auth/register', json={'email': email, 'password': password})
login = post('/api/v1/auth/login', json={'email': email, 'password': password})
wrong = post('/api/v1/auth/login', json={'email': email, 'password': 'WrongPassword!2026'})
data = login.json()
access = data.get('access_token', '')
old = data.get('refresh_token', '')
me = httpx.get(base + '/api/v1/auth/me', headers={'Authorization': 'Bearer ' + access}, timeout=10)
tampered = httpx.get(base + '/api/v1/auth/me', headers={'Authorization': 'Bearer ' + access[:-1] + 'x'}, timeout=10)
rotated = post('/api/v1/auth/refresh', json={'refresh_token': old})
new = rotated.json().get('refresh_token', '')
reused = post('/api/v1/auth/refresh', json={'refresh_token': old})
family = post('/api/v1/auth/refresh', json={'refresh_token': new})
fresh = post('/api/v1/auth/login', json={'email': email, 'password': password})
concurrent_raw = fresh.json().get('refresh_token', '')
def refresh_once():
	return post('/api/v1/auth/refresh', json={'refresh_token': concurrent_raw}).status_code
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
	statuses = sorted(pool.map(lambda _: refresh_once(), range(2)))
print(f'email={email}')
print(f'registration={registration.status_code} duplicate={duplicate.status_code} login={login.status_code} wrong_login={wrong.status_code}')
print(f'me={me.status_code} tampered={tampered.status_code}')
print(f'refresh={rotated.status_code} new_token={new != old} reuse={reused.status_code} family_after_reuse={family.status_code} concurrent={statuses}')
