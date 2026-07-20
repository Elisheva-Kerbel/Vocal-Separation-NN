"""Database package.

Exposes the declarative ``Base`` and the lazy sync engine/session factory, and
imports the P2-002 core domain models so their tables are registered on the shared
``Base.metadata`` (and thus on Alembic's ``target_metadata``) whenever ``app.db`` is
imported. Importing this package still opens no database connection and requires no
``DATABASE_URL``; see ``session`` for why.
"""

from app.db.base import NAMING_CONVENTION, Base
from app.db.session import get_engine, get_sessionmaker
from app.db import models  # noqa: F401  registers the core tables on Base.metadata

__all__ = ["NAMING_CONVENTION", "Base", "get_engine", "get_sessionmaker", "models"]
