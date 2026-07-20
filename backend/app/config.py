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
    # Non-secret storage config (safe to display).
    s3_endpoint_url: str
    s3_bucket: str
    # Credentials — kept out of repr/logs so they cannot leak.
    s3_access_key_id: str = field(repr=False)
    s3_secret_access_key: str = field(repr=False)
    # DB connection string — embeds a password, so it is a secret too.
    database_url: str = field(repr=False)


def load_settings() -> Settings:
    """Read configuration from the environment.

    No connections are opened and no values are logged. Host/port defaults match
    .env.example; the ``S3_*`` credentials and ``DATABASE_URL`` default to empty
    (no secret and no database target baked in). A missing ``DATABASE_URL`` is not
    an error here — /health and every non-DB path must keep working without one.
    """
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        backend_port=int(os.getenv("BACKEND_PORT", "8000")),
        s3_endpoint_url=os.getenv("S3_ENDPOINT_URL", ""),
        s3_bucket=os.getenv("S3_BUCKET", ""),
        s3_access_key_id=os.getenv("S3_ACCESS_KEY_ID", ""),
        s3_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY", ""),
        database_url=os.getenv("DATABASE_URL", ""),
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
