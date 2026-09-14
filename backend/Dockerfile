# StemSpace backend — Phase 0 FastAPI skeleton image.
#
# Minimal Python base that installs the FastAPI backend dependencies, copies the
# app, and runs uvicorn. Phase 0 scope: /health only — no business logic, no DB /
# Redis / storage / queue / AI clients.
FROM python:3.12-slim

# Unbuffered stdout/stderr and no .pyc files — friendlier container logs.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# ffmpeg is required by torchaudio/demucs for audio I/O.
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code and tests (see .dockerignore for what is excluded).
COPY . .

# Container always listens on 8000; docker-compose maps the host BACKEND_PORT.
EXPOSE 8000

# Run the FastAPI /health app. docker-compose overrides this only for the worker.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
