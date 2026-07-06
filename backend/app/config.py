"""Minimal Phase 0 backend configuration.

Reads only the local environment variables the Phase 0 skeleton needs. It opens
and validates NO live connections (PostgreSQL / Redis / MinIO checks belong to
later phases) and never logs or returns secret values — the credential fields are
excluded from the dataclass ``repr`` so they cannot leak into logs, and /health
exposes none of these.

The ``S3_*`` names are the locked storage-config source of truth (see
docs/decisions/DEC-0003 and the S3 abstraction naming); do not introduce
``MINIO_*`` aliases here.
"""

import os
from dataclasses import dataclass, field

# Service identity returned by /health. Not a secret.
SERVICE_NAME = "stemspace-backend"


@dataclass(frozen=True)
class Settings:
    """Immutable snapshot of Phase 0 local configuration."""

    app_env: str
    backend_host: str
    backend_port: int
    # Non-secret storage config (safe to display).
    s3_endpoint_url: str
    s3_bucket: str
    # Credentials — kept out of repr/logs so they cannot leak.
    s3_access_key_id: str = field(repr=False)
    s3_secret_access_key: str = field(repr=False)


def load_settings() -> Settings:
    """Read Phase 0 configuration from the environment.

    No connections are opened and no values are logged. Host/port defaults match
    .env.example; the ``S3_*`` credentials default to empty (no secret baked in).
    """
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        backend_port=int(os.getenv("BACKEND_PORT", "8000")),
        s3_endpoint_url=os.getenv("S3_ENDPOINT_URL", ""),
        s3_bucket=os.getenv("S3_BUCKET", ""),
        s3_access_key_id=os.getenv("S3_ACCESS_KEY_ID", ""),
        s3_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY", ""),
    )
