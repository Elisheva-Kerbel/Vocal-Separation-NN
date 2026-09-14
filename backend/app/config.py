"""Minimal backend configuration.

Reads only the local environment variables the current phases need. It opens and
validates NO live connections (PostgreSQL / Redis / MinIO checks belong to later
phases) and never logs or returns secret values — the credential fields are
excluded from the dataclass ``repr`` so they cannot leak into logs, and /health
exposes none of these.

The ``S3_*`` names are the locked storage-config source of truth (see
docs/decisions/DEC-0003 and the S3 abstraction naming); do not introduce
``MINIO_*`` aliases here.

``DATABASE_URL`` (P2-001 / DEC-0005) is read here and nowhere else: this module is
the single DB-URL source, so DB modules never call ``os.getenv`` themselves. It is
a secret (it embeds a password), so it is repr-hidden like the ``S3_*``
credentials and is never logged, echoed or returned. Loading stays non-fatal when
it is absent — only code that actually needs a database calls
``require_database_url()``, which fails clearly without ever echoing the value.
"""

import os
from dataclasses import dataclass, field

# Service identity returned by /health. Not a secret.
SERVICE_NAME = "stemspace-backend"


class MissingDatabaseUrlError(RuntimeError):
    """Raised when a database is needed but ``DATABASE_URL`` is not configured.

    The message deliberately carries no configuration value: DEC-0005 §7 requires
    that the URL and its password never appear in errors, logs or test output.
    """


@dataclass(frozen=True)
class Settings:
    """Immutable snapshot of local configuration."""

    app_env: str
    backend_host: str
    backend_port: int
    s3_endpoint_url: str
    s3_public_endpoint_url: str
    s3_bucket: str
    s3_region: str
    s3_access_key_id: str = field(repr=False)
    s3_secret_access_key: str = field(repr=False)
    database_url: str = field(repr=False)
    celery_broker_url: str = field(repr=False)
    celery_result_backend: str = field(repr=False)
    max_upload_bytes: int = 100 * 1024 * 1024
    max_duration_seconds: float = 330.0
    free_daily_limit: int = 3
    pro_daily_limit: int = 10
    signed_url_listen_ttl: int = 600
    signed_url_download_ttl: int = 300
    google_client_id: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = field(repr=False, default="")
    smtp_from_email: str = ""
    smtp_from_name: str = "VocalSplit"


def load_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        backend_port=int(os.getenv("BACKEND_PORT", "8000")),
        s3_endpoint_url=os.getenv("S3_ENDPOINT_URL", ""),
        s3_public_endpoint_url=os.getenv("S3_PUBLIC_ENDPOINT_URL", os.getenv("S3_ENDPOINT_URL", "")),
        s3_bucket=os.getenv("S3_BUCKET", ""),
        s3_region=os.getenv("S3_REGION", "us-east-1"),
        s3_access_key_id=os.getenv("S3_ACCESS_KEY_ID", ""),
        s3_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY", ""),
        database_url=os.getenv("DATABASE_URL", ""),
        celery_broker_url=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
        celery_result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
        max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(100 * 1024 * 1024))),
        max_duration_seconds=float(os.getenv("MAX_DURATION_SECONDS", "330")),
        free_daily_limit=int(os.getenv("FREE_DAILY_LIMIT", "3")),
        pro_daily_limit=int(os.getenv("PRO_DAILY_LIMIT", "10")),
        signed_url_listen_ttl=int(os.getenv("SIGNED_URL_LISTEN_TTL", "600")),
        signed_url_download_ttl=int(os.getenv("SIGNED_URL_DOWNLOAD_TTL", "300")),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_from_email=os.getenv("SMTP_FROM_EMAIL", ""),
        smtp_from_name=os.getenv("SMTP_FROM_NAME", "VocalSplit"),
    )


def require_database_url(settings: Settings | None = None) -> str:
    """Return the configured DB URL, or fail clearly if it is missing.

    This is the only supported way for DB code to obtain the URL. It raises
    ``MissingDatabaseUrlError`` when ``DATABASE_URL`` is unset or blank —
    a visible, actionable failure rather than a silent fallback or a default
    connection target. The error names the variable but never its value.
    """
    url = (settings or load_settings()).database_url
    if not url.strip():
        raise MissingDatabaseUrlError(
            "DATABASE_URL is not set. Set it in your local .env file "
            "(see .env.example for the placeholder). Its value is never logged."
        )
    return url
