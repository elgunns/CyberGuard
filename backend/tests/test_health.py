"""Tests for GET /health (FR-24) and the error envelope."""
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.config import Settings
from backend.app.main import create_app
from database.init_db import apply_schema

# A port nothing listens on, so connecting fails straight away. Contains no real credentials.
UNREACHABLE_URL = "postgresql://cyberguard:unused@127.0.0.1:1/cyberguard_test"


def _client(database_url: str, log_dir: Path) -> TestClient:
    settings = Settings(database_url=database_url, test_database_url=database_url, log_dir=log_dir)
    return TestClient(create_app(settings))


def test_health_reports_ok_when_database_works(test_database_url: str, tmp_path: Path):
    apply_schema(test_database_url)
    client = _client(test_database_url, tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == {"status": "ok", "backend": "ok", "database": "ok"}


def test_health_returns_503_degraded_when_database_is_down(tmp_path: Path):
    client = _client(UNREACHABLE_URL, tmp_path)

    response = client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["data"]["status"] == "degraded"
    assert body["data"]["backend"] == "ok"
    assert body["data"]["database"] == "unreachable"
    assert "unused" not in response.text  # no connection details in the response


def test_unknown_route_uses_error_envelope(tmp_path: Path):
    client = _client(UNREACHABLE_URL, tmp_path)

    response = client.get("/no-such-endpoint")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error": {"code": "NOT_FOUND", "message": "The requested endpoint does not exist."},
    }
