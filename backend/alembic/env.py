"""Alembic environment for StemSpace (P2-001 scaffold).

Wires Alembic to the one shared ``Base.metadata`` (DEC-0005 §6) and takes the
database URL from app.config — the single DB-URL source — so no credential is
committed and DATABASE_URL is never echoed into logs or errors.

Local Compose Postgres only. This file runs migrations only when Alembic invokes
it; nothing here runs at app or container startup.
"""

from logging.config import fileConfig

from alembic import context

from app.config import require_database_url
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The same MetaData object the models will use — not a copy, so autogenerate and
# runtime cannot drift apart. Empty in P2-001: no entities exist yet.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL without connecting to a database."""
    context.configure(
        url=require_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live local database."""
    # Imported here so offline mode neither builds an engine nor needs a database.
    from app.db.session import get_engine

    with get_engine().connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
