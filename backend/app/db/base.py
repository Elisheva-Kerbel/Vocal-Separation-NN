"""SQLAlchemy declarative base and shared metadata (P2-001 scaffold).

Defines the SQLAlchemy 2.x ``DeclarativeBase`` and the single shared ``MetaData``
that every future domain model and Alembic itself use, per DEC-0005.

No entities are defined here. P2-001 is the DB scaffold only: domain models
arrive in P2-002, which stays blocked until the Song / SeparationJob state values
and entity fields are decided. Importing this module opens no DB connection.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# DEC-0005 §6: constraint and index names are decided here, never assigned by the
# database backend. Deterministic names keep Alembic autogenerate diffs stable and
# keep downgrade paths able to reference a constraint by name.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base for all future domain models.

    Carries the one shared ``MetaData`` that Alembic's ``target_metadata`` points
    at, so autogenerate and runtime cannot drift apart. No mixins are defined:
    per DEC-0005 §5 any shared ID/timestamp mixin is introduced when models are
    designed and justified, not pre-built here.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
