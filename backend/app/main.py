"""StemSpace backend — FastAPI application.

Exposes ``GET /health`` (Phase 0), the two local-demo routes under ``/demo``
(FAST-DEMO-003, authorized by ``docs/decisions/DEC-0009-local-demo-vertical-slice.md``)
and the four local MVP auth routes under ``/auth`` (Phase 3, authorized by
``docs/decisions/DEC-0010-phase-3-auth-contract.md``).

Only ``/auth`` touches the database, and only per request — importing this module
still opens no connection. No Redis / MinIO / queue access anywhere. The demo
stays open: signing in is not required to use it. /health opens no connections and
returns no configuration or secret values.
"""

from fastapi import FastAPI

from app.auth import router as auth_router
from app.config import SERVICE_NAME
from app.demo import router as demo_router

app = FastAPI(title="StemSpace Backend", version="0.1.0")
app.include_router(demo_router)
app.include_router(auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness smoke test.

    Returns a minimal, secret-free status payload. Does not touch PostgreSQL,
    Redis, MinIO, the queue, storage, the AI model, the filesystem, or the
    network.
    """
    return {"status": "ok", "service": SERVICE_NAME}
