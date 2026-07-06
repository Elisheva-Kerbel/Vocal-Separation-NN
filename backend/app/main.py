"""StemSpace backend — Phase 0 FastAPI skeleton.

Exposes a single ``GET /health`` smoke-test endpoint. Phase 0 boundary: no other
application routes, no auth, no DB / Redis / MinIO / queue / AI access. /health
opens no connections and returns no configuration or secret values.
"""

from fastapi import FastAPI

from app.config import SERVICE_NAME

app = FastAPI(title="StemSpace Backend", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness smoke test.

    Returns a minimal, secret-free status payload. Does not touch PostgreSQL,
    Redis, MinIO, the queue, storage, the AI model, the filesystem, or the
    network.
    """
    return {"status": "ok", "service": SERVICE_NAME}
