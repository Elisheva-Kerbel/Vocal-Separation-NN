"""P2-002 constraint / index tests.

Prove the DEC-0006 §10 uniqueness constraints, the SongTag composite primary key,
the required indexes and the still-active DEC-0005 naming convention. Metadata
inspection only — no engine, no connection.
"""

from sqlalchemy import UniqueConstraint

from app.db import models  # noqa: F401  ensures the tables are registered
from app.db.base import NAMING_CONVENTION, Base

EXPECTED_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# (table, ordered columns) for each required composite UNIQUE. Deterministic NAMES
# are asserted authoritatively in test_alembic_models_migration.py; here we prove the
# structural constraint exists (independent of convention-name materialisation).
EXPECTED_COMPOSITE_UNIQUES = {
    ("audio_files", ("song_id", "purpose")),
    ("usage_events", ("song_id", "event_type")),
    ("daily_usage", ("user_id", "usage_date")),
}

# name -> (table, ordered columns). Looked up by (table, columns), not by name.
EXPECTED_INDEXES = {
    "ix_songs_user_id": ("songs", ("user_id", "created_at")),
    "ix_songs_status": ("songs", ("status",)),
    "ix_audio_files_song_id": ("audio_files", ("song_id",)),
    "ix_separation_jobs_song_id": ("separation_jobs", ("song_id", "created_at")),
    "ix_separation_jobs_status": ("separation_jobs", ("status",)),
    "ix_song_tags_tag_id": ("song_tags", ("tag_id",)),
    "ix_usage_events_user_id": ("usage_events", ("user_id", "created_at")),
    "ix_daily_usage_usage_date": ("daily_usage", ("usage_date",)),
}


def _has_unique(table_name: str, cols: tuple[str, ...]) -> bool:
    table = Base.metadata.tables[table_name]
    return any(
        isinstance(c, UniqueConstraint)
        and tuple(col.name for col in c.columns) == cols
        for c in table.constraints
    )


def test_naming_convention_still_active():
    assert dict(Base.metadata.naming_convention) == EXPECTED_NAMING_CONVENTION
    assert NAMING_CONVENTION == EXPECTED_NAMING_CONVENTION


def test_single_column_unique_flags():
    assert Base.metadata.tables["users"].c["email"].unique is True
    assert Base.metadata.tables["tags"].c["slug"].unique is True
    assert Base.metadata.tables["audio_files"].c["storage_key"].unique is True


def test_composite_unique_constraints_exist():
    for table_name, cols in EXPECTED_COMPOSITE_UNIQUES:
        assert _has_unique(table_name, cols), f"missing unique {cols} on {table_name}"


def test_audio_file_purpose_uniqueness():
    assert _has_unique("audio_files", ("song_id", "purpose"))


def test_usage_event_idempotency_uniqueness():
    # DEC-0006 §8: at most one billable finalisation per song.
    assert _has_unique("usage_events", ("song_id", "event_type"))


def test_daily_usage_uniqueness():
    assert _has_unique("daily_usage", ("user_id", "usage_date"))


def test_song_tag_composite_primary_key():
    pk = Base.metadata.tables["song_tags"].primary_key
    assert [c.name for c in pk.columns] == ["song_id", "tag_id"]


def test_required_indexes_exist_with_expected_columns():
    existing = {
        (table.name, tuple(c.name for c in idx.columns))
        for table in Base.metadata.tables.values()
        for idx in table.indexes
    }
    for name, (table_name, columns) in EXPECTED_INDEXES.items():
        assert (table_name, columns) in existing, f"missing index for {name}"
