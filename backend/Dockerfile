# StemSpace backend — Phase 0 skeleton image.
#
# A minimal Python base for the FastAPI backend that arrives in P0-003. Phase 0
# intentionally ships NO application code, NO dependency install and NO /health
# endpoint — this image only needs to build. P0-003 extends it to COPY
# requirements.txt + app/ and run uvicorn.
FROM python:3.12-slim

# Unbuffered stdout/stderr and no .pyc files — friendlier container logs.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Phase 0 default command (docker-compose overrides it per service). No app yet.
CMD ["python", "-c", "print('stemspace backend skeleton — no app yet (P0-002; FastAPI arrives in P0-003)')"]
