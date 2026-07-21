"""P2-004 seed-tags tests (DEC-0008 §2, §4, §10).

Prove the seed inserts EXACTLY the four approved placeholder tags, is idempotent by
slug (running twice creates no duplicates and no error), inserts no non-tag data,
and its only output is a safe, secret-free count summary. Uses SQLite in-memory
built via ``metadata.create_all()`` (DEC-0008 §5) — no live PostgreSQL required.
"""

import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db import models  # noqa: F401  registers the 8 core tables on Base.metadata
from app.db.base import Base
from app.db.models import Tag

import scripts.seed_tags as seed_module
from scripts.seed_tags import SEED_TAGS, format_summary, seed_tags

EXPECTED_TAGS = {
    ("vocals", "Vocals"),
    ("background", "Background"),
    ("instrumental", "Instrumental"),
    ("demo", "Demo"),
}


@pytest.fixture
def sqlite_session():
    # In-memory SQLite (SingletonThreadPool keeps one shared connection), schema
    # built from the shared metadata — no migration, no live PostgreSQL.
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def _tag_count(session) -> int:
    return session.scalar(select(func.count()).select_from(Tag))


def test_seed_tag_list_is_exactly_the_four_dec0008_tags():
    assert len(SEED_TAGS) == 4
    assert set(SEED_TAGS) == EXPECTED_TAGS


def test_seed_inserts_the_four_tags(sqlite_session):
    seed_tags(sqlite_session)
    rows = sqlite_session.execute(select(Tag.slug, Tag.name)).all()
    assert {(r.slug, r.name) for r in rows} == EXPECTED_TAGS
    assert _tag_count(sqlite_session) == 4


def test_seed_is_idempotent(sqlite_session):
    first = seed_tags(sqlite_session)
    second = seed_tags(sqlite_session)
    # Running twice -> still exactly four rows, no duplicates, no error.
    assert _tag_count(sqlite_session) == 4
    assert first == {"created": 4, "skipped": 0, "total": 4}
    assert second == {"created": 0, "skipped": 4, "total": 4}


def test_seed_inserts_no_non_tag_data(sqlite_session):
    seed_tags(sqlite_session)
    # Only the tags table is populated; every other core table stays empty.
    for table_name, table in Base.metadata.tables.items():
        n = sqlite_session.scalar(select(func.count()).select_from(table))
        expected = 4 if table_name == "tags" else 0
        assert n == expected, f"{table_name} has {n} rows (expected {expected})"


def test_seed_function_is_silent(sqlite_session):
    # seed_tags itself prints nothing (no accidental leak via stdout).
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        seed_tags(sqlite_session)
    assert buffer.getvalue() == ""


def test_seed_summary_is_safe_counts_only(sqlite_session):
    summary = seed_tags(sqlite_session)
    assert set(summary) == {"created", "skipped", "total"}
    assert all(isinstance(v, int) for v in summary.values())


def test_seed_output_line_contains_no_secrets():
    text = format_summary({"created": 4, "skipped": 0, "total": 4})
    assert text == "seed_tags: created=4 skipped=0 total=4"
    lowered = text.lower()
    for forbidden in ("://", "@", "password", "secret", "token", "database_url", "postgres"):
        assert forbidden not in lowered, forbidden


def test_seed_script_pulls_no_forbidden_clients():
    src = Path(seed_module.__file__).read_text(encoding="utf-8")
    for forbidden in ("redis", "celery", "boto3", "minio", "torch", "librosa", "soundfile"):
        assert forbidden not in src, forbidden
