"""Phase 0 /health smoke tests.

Prove the endpoint is reachable, returns HTTP 200 with the minimal safe payload,
leaks no secrets, and that no out-of-scope application routes exist.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "stemspace-backend"}


def test_health_exposes_no_secrets():
    # /health must never leak credentials, keys or connection strings
    # (docs/decisions/DEC-0003 + secrets policy).
    body = client.get("/health").text.lower()
    for leaked in (
        "secret",
        "password",
        "access_key",
        "s3_",
        "database_url",
        "redis",
        "postgres",
        "minio",
    ):
        assert leaked not in body


def test_no_out_of_scope_routes():
    # Phase 0 boundary: /health is the only application route (FastAPI's own
    # /docs, /openapi.json etc. are framework defaults, not added routers).
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/health" in paths
    for forbidden in ("/upload", "/auth", "/login", "/songs", "/jobs", "/stems"):
        assert forbidden not in paths
