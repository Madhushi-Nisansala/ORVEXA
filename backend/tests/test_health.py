import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.exceptions import unhandled_exception_handler
from app.main import app

client = TestClient(app)


@pytest.mark.parametrize('path', ['/', '/api/v1/'])
def test_root_endpoint(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert response.json()['application'] == 'ORVEXA'
    assert response.json()['version'] == '0.1.0'
    assert response.json()['status'] == 'operational'


def test_health_endpoint_reports_connected_database(monkeypatch: pytest.MonkeyPatch) -> None:
    async def connected() -> bool:
        return True

    monkeypatch.setattr('app.api.v1.endpoints.system.check_database_connection', connected)

    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {
        'status': 'healthy',
        'application': 'ORVEXA',
        'version': '0.1.0',
        'database': 'connected',
    }


def test_health_and_readiness_report_database_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    async def unavailable() -> bool:
        return False

    monkeypatch.setattr('app.api.v1.endpoints.system.check_database_connection', unavailable)

    health = client.get('/api/v1/health')
    readiness = client.get('/api/v1/ready')

    assert health.status_code == 503
    assert health.json()['status'] == 'degraded'
    assert health.json()['database'] == 'unavailable'
    assert readiness.status_code == 503
    assert readiness.json() == {'status': 'not_ready', 'checks': {'database': 'unavailable'}}


def test_database_url_escapes_password() -> None:
    settings = Settings(POSTGRES_PASSWORD='p@ss:word/with?chars', POSTGRES_DB='orvexa_db')

    assert settings.get_database_url() == 'postgresql+asyncpg://orvexa:p%40ss%3Aword%2Fwith%3Fchars@localhost:5432/orvexa_db'


def test_unhandled_exception_response_is_safe() -> None:
    request = client.build_request('GET', '/')
    response = client.send(request)

    assert response.status_code == 200
    assert 'traceback' not in response.text.lower()
