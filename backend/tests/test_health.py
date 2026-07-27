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
    # Route boundary guard, deliberately re-scoped by FAST-DEMO-003 (not removed):
    # DEC-0009 §5 allows exactly two local-demo routes under /demo, on top of
    # /health. Everything else stays out of scope. (FastAPI's own /docs,
    # /openapi.json etc. are framework defaults, not added routers.)
    # The OpenAPI schema is the reliable list of *application* routes: app.routes
    # keeps an included router as one opaque entry, and also carries FastAPI's own
    # /docs and /openapi.json. Exact equality proves no extra route slipped in.
    paths = set(app.openapi()["paths"])
    assert paths == {
        "/health",
        "/demo/separate",
        "/demo/jobs/{job_id}/stems/{stem}",
    }

    # No product route outside the /demo prefix — including these by exact path.
    for forbidden in (
        "/upload",
        "/auth",
        "/login",
        "/songs",
        "/library",
        "/admin",
        "/jobs",
        "/stems",
    ):
        assert forbidden not in paths
