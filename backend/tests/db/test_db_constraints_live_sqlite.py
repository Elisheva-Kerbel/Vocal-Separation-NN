"""P2-004 live constraint tests on SQLite in-memory (DEC-0008 §5, §7, §10).

Prove the database itself REJECTS a duplicate for each already-defined uniqueness
key (a real constraint violation, not application-level checking), using an
in-memory SQLite engine built from the shared metadata via ``metadata.create_all()``.
SQLite enforces UNIQUE, composite PRIMARY KEY and CHECK constraints, so these keys
are faithfully testable here; no live PostgreSQL is required (DEC-0008 §6).

Inserts use SQLAlchemy Core so the assertion targets the DB constraint directly,
independent of any ORM identity-map behaviour. Foreign-key parents are not created:
SQLite leaves FK enforcement off by default and these tests concern UNIQUE/PK/CHECK
only, so unparented FK values are harmless here (DEC-0008 §7 limitation clause).
"""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from app.db import models  # noqa: F401  registers the 8 core tables on Base.metadata
from app.db.base import Base
from app.db.models import AudioFile, DailyUsage, SongTag, Tag, UsageEvent


@pytest.fixture
def sqlite_engine():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def _insert(engine, table, **values):
    with engine.begin() as conn:
        conn.execute(table.insert().values(**values))


def test_tag_slug_uniqueness_enforced_by_db(sqlite_engine):
    t = Tag.__table__
    _insert(sqlite_engine, t, id=uuid4(), slug="dup-slug", name="First")
    with pytest.raises(IntegrityError):
        _insert(sqlite_engine, t, id=uuid4(), slug="dup-slug", name="Second")


def test_song_tag_composite_uniqueness_enforced_by_db(sqlite_engine):
    t = SongTag.__table__
    song_id, tag_id = uuid4(), uuid4()
    _insert(sqlite_engine, t, song_id=song_id, tag_id=tag_id)
    with pytest.raises(IntegrityError):
        _insert(sqlite_engine, t, song_id=song_id, tag_id=tag_id)


def test_usage_event_uniqueness_enforced_by_db(sqlite_engine):
    # DEC-0006 §8 / R-006: at most one billable finalisation per song.
    t = UsageEvent.__table__
    song_id, user_id = uuid4(), uuid4()
    _insert(
        sqlite_engine, t,
        id=uuid4(), user_id=user_id, song_id=song_id,
        event_type="separation_succeeded",
    )
    with pytest.raises(IntegrityError):
        _insert(
            sqlite_engine, t,
            id=uuid4(), user_id=user_id, song_id=song_id,
            event_type="separation_succeeded",
        )


def test_daily_usage_uniqueness_enforced_by_db(sqlite_engine):
    t = DailyUsage.__table__
    user_id, day = uuid4(), date(2026, 1, 1)
    _insert(sqlite_engine, t, id=uuid4(), user_id=user_id, usage_date=day)
    with pytest.raises(IntegrityError):
        _insert(sqlite_engine, t, id=uuid4(), user_id=user_id, usage_date=day)


def test_audio_file_song_id_purpose_uniqueness_enforced_by_db(sqlite_engine):
    # At most one original / vocals / background per song. Distinct storage_key
    # values isolate the (song_id, purpose) violation from the storage_key UNIQUE.
    t = AudioFile.__table__
    song_id = uuid4()
    _insert(
        sqlite_engine, t,
        id=uuid4(), song_id=song_id, purpose="original",
        storage_key="song/x/original/1", content_type="audio/wav", byte_size=1,
    )
    with pytest.raises(IntegrityError):
        _insert(
            sqlite_engine, t,
            id=uuid4(), song_id=song_id, purpose="original",
            storage_key="song/x/original/2", content_type="audio/wav", byte_size=2,
        )
