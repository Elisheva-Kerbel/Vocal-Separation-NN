"""Sync SQLAlchemy engine and session factory (P2-001 scaffold).

Synchronous ``Session`` / ``sessionmaker`` over the psycopg3 sync driver, per
DEC-0005 §4. There is no async SQLAlchemy here.

Importing this module opens NO database connection: the engine is created on
first use, not at import time, so /health, the AI boundary and the test suite all
keep working with no database and no ``DATABASE_URL`` present. The URL comes from
app.config (the single DB-URL source) and is never logged or echoed.

Nothing here runs migrations. Migrations are run deliberately via Alembic, never
implicitly at app or container startup.
"""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import require_database_url

# Created lazily on first use so that import stays connection-free and does not
# require DATABASE_URL to be set.
_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Return the process-wide sync engine, creating it on first call.

    Fails via ``MissingDatabaseUrlError`` when ``DATABASE_URL`` is not configured.
    Creating the engine still opens no socket — SQLAlchemy connects lazily when a
    connection is first checked out of the pool.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(require_database_url())
    return _engine


def get_sessionmaker() -> sessionmaker[Session]:
    """Return the process-wide sync session factory, creating it on first call."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory
