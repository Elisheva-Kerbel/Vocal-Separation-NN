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
    # Route boundary guard, deliberately re-scoped twice and never weakened:
    # FAST-DEMO-003 allowed exactly two local-demo routes under /demo (DEC-0009
    # §5), and Phase 3 allows exactly the four auth routes under /auth (DEC-0010
    # §4, approved for Local MVP). Everything else stays out of scope. (FastAPI's
    # own /docs, /openapi.json etc. are framework defaults, not added routers.)
    # The OpenAPI schema is the reliable list of *application* routes: app.routes
    # keeps an included router as one opaque entry, and also carries FastAPI's own
    # /docs and /openapi.json. Exact equality proves no extra route slipped in.
    paths = set(app.openapi()["paths"])
    assert paths == {
        "/health",
        "/demo/separate",
        "/demo/jobs/{job_id}/stems/{stem}",
        "/auth/signup",
        "/auth/login",
        "/auth/logout",
        "/auth/me",
    }

    # No product route outside the /demo and /auth prefixes — by exact path. Phase
    # 4+ surfaces (upload, songs, library, admin, jobs, stems) remain forbidden,
    # and so do the auth features Phase 3 explicitly excludes (DEC-0010 §6).
    for forbidden in (
        "/upload",
        "/songs",
        "/library",
        "/admin",
        "/jobs",
        "/stems",
        "/auth/forgot-password",
        "/auth/reset-password",
        "/auth/verify-email",
        "/auth/oauth",
        "/auth/token",
    ):
        assert forbidden not in paths


def test_every_route_is_health_demo_or_auth():
    # The prefix-level companion to the exact-set check above: nothing may live
    # outside the three authorized surfaces, whatever it is called.
    for path in app.openapi()["paths"]:
        assert path == "/health" or path.startswith(("/demo/", "/auth/")), path
