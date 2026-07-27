"""StemSpace backend — FastAPI application.

Exposes ``GET /health`` (Phase 0) plus the two local-demo routes under ``/demo``
(FAST-DEMO-003, authorized by ``docs/decisions/DEC-0009-local-demo-vertical-slice.md``).
No auth, no DB / Redis / MinIO / queue access. /health opens no connections and
returns no configuration or secret values.
"""

from fastapi import FastAPI

from app.config import SERVICE_NAME
from app.demo import router as demo_router

app = FastAPI(title="StemSpace Backend", version="0.1.0")
app.include_router(demo_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness smoke test.

    Returns a minimal, secret-free status payload. Does not touch PostgreSQL,
    Redis, MinIO, the queue, storage, the AI model, the filesystem, or the
    network.
    """
    return {"status": "ok", "service": SERVICE_NAME}
