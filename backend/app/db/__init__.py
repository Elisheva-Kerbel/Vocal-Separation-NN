"""Database package (P2-001 scaffold).

Exposes the declarative ``Base`` and the lazy sync engine/session factory.
Importing this package opens no database connection and requires no
``DATABASE_URL``; see ``session`` for why. No domain models live here — those
arrive in P2-002.
"""

from app.db.base import NAMING_CONVENTION, Base
from app.db.session import get_engine, get_sessionmaker

__all__ = ["NAMING_CONVENTION", "Base", "get_engine", "get_sessionmaker"]
