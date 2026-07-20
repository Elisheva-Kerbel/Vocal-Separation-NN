"""P2-002 domain-model shape tests.

Prove that exactly the 8 DEC-0006 core tables are registered on the shared
``Base.metadata`` (no deferred tables), that each has exactly its DEC-0006 columns,
that enum CHECK values match DEC-0006 §3-enums verbatim, that foreign keys point at
the right tables, and that the timestamp convention (created_at on all; updated_at on
mutable tables only) holds. All checks inspect metadata only — no engine, no
connection.
"""

import re

from sqlalchemy import CheckConstraint

from app.db import models  # noqa: F401  ensures the tables are registered
from app.db.base import Base

CORE_TABLES = {
    "users",
    "songs",
    "audio_files",
    "separation_jobs",
    "tags",
    "song_tags",
    "usage_events",
    "daily_usage",
}

DEFERRED_TABLES = {
    "ratings",
    "coupons",
    "coupon_redemptions",
    "signed_url_grants",
    "content_reports",
    "admin_audit_events",
}

EXPECTED_COLUMNS = {
    "users": {"id", "email", "status", "created_at", "updated_at"},
    "songs": {"id", "user_id", "title", "status", "created_at", "updated_at"},
    "audio_files": {
        "id",
        "song_id",
        "purpose",
        "storage_key",
        "content_type",
        "byte_size",
        "checksum_sha256",
        "duration_seconds",
        "original_filename",
        "created_at",
        "updated_at",
    },
    "separation_jobs": {
        "id",
        "song_id",
        "status",
        "model_tier",
        "error_message",
        "started_at",
        "finished_at",
        "created_at",
        "updated_at",
    },
    "tags": {"id", "slug", "name", "created_at", "updated_at"},
    "song_tags": {"song_id", "tag_id", "created_at"},
    "usage_events": {
        "id",
        "user_id",
        "song_id",
        "separation_job_id",
        "event_type",
        "created_at",
    },
    "daily_usage": {
        "id",
        "user_id",
        "usage_date",
        "successful_count",
        "created_at",
        "updated_at",
    },
}

# DEC-0006 §3-enums — table -> exact allowed value set(s) that a CHECK must enforce.
# Matched by value-set (unique per constraint), so this is independent of when
# SQLAlchemy materialises the convention constraint name.
EXPECTED_ENUMS = {
    ("users", "status"): {"active", "blocked", "deleted"},
    ("songs", "status"): {"uploaded", "processing", "ready", "failed"},
    ("audio_files", "purpose"): {"original", "vocals", "background"},
    ("separation_jobs", "status"): {
        "queued",
        "running",
        "succeeded",
        "failed",
        "canceled",
    },
    ("separation_jobs", "model_tier"): {"basic"},
    ("usage_events", "event_type"): {"separation_succeeded"},
}

# column -> referent table.
EXPECTED_FKS = {
    ("songs", "user_id"): "users",
    ("audio_files", "song_id"): "songs",
    ("separation_jobs", "song_id"): "songs",
    ("song_tags", "song_id"): "songs",
    ("song_tags", "tag_id"): "tags",
    ("usage_events", "user_id"): "users",
    ("usage_events", "song_id"): "songs",
    ("usage_events", "separation_job_id"): "separation_jobs",
    ("daily_usage", "user_id"): "users",
}

MUTABLE_TABLES = {
    "users",
    "songs",
    "audio_files",
    "separation_jobs",
    "tags",
    "daily_usage",
}
APPEND_ONLY_TABLES = {"song_tags", "usage_events"}


def _check_value_sets(table_name: str) -> list[set[str]]:
    table = Base.metadata.tables[table_name]
    return [
        set(re.findall(r"'([^']*)'", str(constraint.sqltext)))
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    ]


def test_exactly_the_core_tables_are_registered():
    assert set(Base.metadata.tables) == CORE_TABLES


def test_no_deferred_tables_exist():
    assert DEFERRED_TABLES.isdisjoint(set(Base.metadata.tables))


def test_expected_columns_per_entity():
    for table_name, expected in EXPECTED_COLUMNS.items():
        actual = set(Base.metadata.tables[table_name].columns.keys())
        assert actual == expected, f"{table_name}: {actual ^ expected}"


def test_enum_check_values_match_dec_0006():
    for (table_name, _column), expected in EXPECTED_ENUMS.items():
        assert expected in _check_value_sets(table_name), f"{table_name}: {expected}"


def test_foreign_keys_point_at_the_right_tables():
    for (table_name, column), referent in EXPECTED_FKS.items():
        fks = Base.metadata.tables[table_name].c[column].foreign_keys
        assert fks, f"{table_name}.{column} has no FK"
        assert {fk.column.table.name for fk in fks} == {referent}


def test_orm_relationships_configure_cleanly():
    # Forces relationship() resolution (back_populates pairing, join inference);
    # a misconfigured relationship raises here rather than in a later phase.
    from sqlalchemy.orm import configure_mappers

    configure_mappers()


def test_created_at_on_every_table():
    for table_name in CORE_TABLES:
        assert "created_at" in Base.metadata.tables[table_name].columns


def test_updated_at_only_on_mutable_tables():
    for table_name in MUTABLE_TABLES:
        assert "updated_at" in Base.metadata.tables[table_name].columns
    for table_name in APPEND_ONLY_TABLES:
        assert "updated_at" not in Base.metadata.tables[table_name].columns


def test_timestamps_are_timezone_aware():
    for table_name in CORE_TABLES:
        col = Base.metadata.tables[table_name].columns["created_at"]
        assert getattr(col.type, "timezone", False) is True
