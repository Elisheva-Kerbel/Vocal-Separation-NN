"""P3-001 auth column / sessions-table tests (DEC-0010 §3).

Prove the four account columns and the ``sessions`` table exist with exactly the
approved shape, that the single Phase 3 migration is a well-formed, deterministic
revision on top of P2-002, and that the schema stores no raw session token and no
plaintext password. Metadata + filesystem inspection, plus live UNIQUE checks on
in-memory SQLite (DEC-0008 §5–§7) — no PostgreSQL, no engine to a real database.
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from app.db import models  # noqa: F401  ensures the tables are registered
from app.db.base import NAMING_CONVENTION, Base
from app.db.models import User, UserSession

BACKEND_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
MIGRATION = (
    BACKEND_DIR / "alembic" / "versions" / "p3_001_auth_columns_and_sessions.py"
)
REVISION = "p3_001_auth_columns_and_sessions"

NEW_USER_COLUMNS = {
    "password_hash",
    "profile_visibility",
    "preferred_language",
    "email_opt_in",
}
SESSION_COLUMNS = {"id", "user_id", "token_hash", "expires_at", "created_at"}

# Column names that would mean a credential or a raw token is being persisted.
FORBIDDEN_COLUMN_NAMES = {
    "password",
    "plaintext_password",
    "session_token",
    "token",
    "raw_token",
    "secret",
    "api_key",
}


def _migration_text() -> str:
    return MIGRATION.read_text(encoding="utf-8")


@pytest.fixture
def sqlite_engine():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


# --- users columns ------------------------------------------------------------


def test_users_gained_exactly_the_four_account_columns():
    columns = set(Base.metadata.tables["users"].columns.keys())
    assert NEW_USER_COLUMNS <= columns
    assert columns.isdisjoint(FORBIDDEN_COLUMN_NAMES)


def test_password_hash_is_a_required_string_column():
    column = Base.metadata.tables["users"].c["password_hash"]
    assert column.nullable is False
    assert column.type.length == 255
    # No server default: there is no shared or empty fallback credential.
    assert column.server_default is None


def test_account_columns_are_private_and_opt_in_by_default():
    users = Base.metadata.tables["users"]
    assert users.c["profile_visibility"].nullable is False
    assert "hidden" in str(users.c["profile_visibility"].server_default.arg)
    assert users.c["email_opt_in"].nullable is False
    assert users.c["email_opt_in"].server_default is not None
    assert users.c["preferred_language"].nullable is True


def test_user_status_values_are_unchanged():
    # Phase 3 reuses the existing status enum rather than adding another one.
    values = {
        value
        for constraint in Base.metadata.tables["users"].constraints
        for value in re.findall(r"'([^']*)'", str(getattr(constraint, "sqltext", "")))
    }
    assert {"active", "blocked", "deleted"} <= values


# --- sessions table -----------------------------------------------------------


def test_sessions_table_has_exactly_the_approved_columns():
    columns = set(Base.metadata.tables["sessions"].columns.keys())
    assert columns == SESSION_COLUMNS
    assert columns.isdisjoint(FORBIDDEN_COLUMN_NAMES)


def test_sessions_stores_only_a_token_hash():
    column = Base.metadata.tables["sessions"].c["token_hash"]
    assert column.nullable is False
    assert column.unique is True
    # 64 hex characters — exactly one SHA-256 digest, not a 43-char token.
    assert column.type.length == 64


def test_sessions_user_id_is_indexed_and_points_at_users():
    column = Base.metadata.tables["sessions"].c["user_id"]
    assert {fk.column.table.name for fk in column.foreign_keys} == {"users"}
    assert any(
        tuple(c.name for c in index.columns) == ("user_id",)
        for index in Base.metadata.tables["sessions"].indexes
    )


def test_token_hash_uniqueness_is_enforced_by_the_database(sqlite_engine):
    digest = "a" * 64
    expires_at = datetime(2030, 1, 1, tzinfo=timezone.utc)
    table = UserSession.__table__
    with sqlite_engine.begin() as conn:
        conn.execute(
            table.insert().values(
                id=uuid4(), user_id=uuid4(), token_hash=digest, expires_at=expires_at
            )
        )
    with pytest.raises(IntegrityError):
        with sqlite_engine.begin() as conn:
            conn.execute(
                table.insert().values(
                    id=uuid4(),
                    user_id=uuid4(),
                    token_hash=digest,
                    expires_at=expires_at,
                )
            )


def test_profile_visibility_check_is_enforced_by_the_database(sqlite_engine):
    with pytest.raises(IntegrityError):
        with sqlite_engine.begin() as conn:
            conn.execute(
                User.__table__.insert().values(
                    id=uuid4(),
                    email="visibility@example.test",
                    status="active",
                    password_hash="scrypt$16384$8$1$c2FsdA==$aGFzaA==",
                    profile_visibility="everyone",
                )
            )


# --- the single Phase 3 migration --------------------------------------------


def test_exactly_one_phase_3_migration_exists():
    versions = MIGRATION.parent
    assert MIGRATION.is_file()
    assert sorted(p.name for p in versions.glob("p3_*.py")) == [MIGRATION.name]


def test_migration_is_a_linear_revision_on_top_of_p2_002():
    script = ScriptDirectory.from_config(Config(str(ALEMBIC_INI)))
    revision = script.get_revision(REVISION)
    assert revision.down_revision == "p2_002_core_domain_models"
    assert list(script.get_heads()) == [REVISION]


def test_migration_creates_only_the_sessions_table():
    assert set(re.findall(r'op\.create_table\(\s*"([^"]+)"', _migration_text())) == {
        "sessions"
    }


def test_migration_adds_exactly_the_four_user_columns():
    added = set(
        re.findall(r'op\.add_column\(\s*"users",\s*sa\.Column\(\s*"([^"]+)"', _migration_text())
    )
    assert added == NEW_USER_COLUMNS


def test_migration_uses_deterministic_convention_names():
    text = _migration_text()
    for name in (
        "pk_sessions",
        "fk_sessions_user_id_users",
        "uq_sessions_token_hash",
        "ix_sessions_user_id",
    ):
        assert name in text, f"missing deterministic name: {name}"
    # No PostgreSQL-autogenerated names, and no double-prefixed name from writing
    # an already-expanded constraint name where the convention key belongs.
    assert "_pkey" not in text
    assert "ck_users_ck_users" not in text


def test_check_constraint_name_resolves_the_same_on_create_and_drop():
    # Alembic applies the DEC-0005 convention (carried over from Base.metadata by
    # env.py) to constraints it builds, so the migration passes the convention KEY
    # on both sides. Both therefore resolve to one deterministic name.
    assert _migration_text().count('"profile_visibility_allowed"') == 2
    assert (
        NAMING_CONVENTION["ck"]
        % {"table_name": "users", "constraint_name": "profile_visibility_allowed"}
        == "ck_users_profile_visibility_allowed"
    )


def test_migration_is_reversible():
    text = _migration_text()
    for dropped in ("password_hash", "profile_visibility", "preferred_language", "email_opt_in"):
        assert f'op.drop_column("users", "{dropped}")' in text
    assert 'op.drop_table("sessions")' in text
    assert 'op.drop_constraint("profile_visibility_allowed", "users"' in text


def test_migration_embeds_no_credential_url_or_seed_account():
    lowered = _migration_text().lower()
    assert "://" not in lowered
    assert "database_url" not in lowered
    # No seed user, no fixture account, no default password (P3-001).
    assert "op.bulk_insert" not in lowered
    assert "insert into" not in lowered
    assert "scrypt$" not in lowered
