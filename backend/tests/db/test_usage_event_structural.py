"""P2-004 structural failed-processing guard (DEC-0008 §8, §10).

Failed processing must never count toward billable usage (R-005). In Phase 2 there
is NO finalizer/business logic, so this is asserted STRUCTURALLY only — behavioral
finalizer tests are deferred to P5/P7 where the logic exists (DEC-0008 §8):

- ``UsageEvent.event_type`` allows only ``separation_succeeded`` (metadata CHECK and
  a live SQLite rejection of any other value);
- there is no billable event type for failed/canceled jobs;
- no P2 application code creates a ``UsageEvent`` at all — no finalizer exists.
"""

import re
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import CheckConstraint, create_engine
from sqlalchemy.exc import IntegrityError

import app
from app.db import models  # noqa: F401  registers the 8 core tables on Base.metadata
from app.db.base import Base
from app.db.models import UsageEvent

APP_DIR = Path(app.__file__).resolve().parent

ALLOWED_EVENT_TYPES = {"separation_succeeded"}


def _check_value_sets(table):
    return [
        set(re.findall(r"'([^']*)'", str(c.sqltext)))
        for c in table.constraints
        if isinstance(c, CheckConstraint)
    ]


@pytest.fixture
def sqlite_engine():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_event_type_check_allows_only_separation_succeeded():
    table = Base.metadata.tables["usage_events"]
    assert ALLOWED_EVENT_TYPES in _check_value_sets(table)


def test_no_billable_event_type_for_failed_or_canceled():
    table = Base.metadata.tables["usage_events"]
    allowed = set().union(*_check_value_sets(table))
    # No failed/canceled/error billing event exists.
    for banned in ("failed", "canceled", "cancelled", "error", "separation_failed"):
        assert banned not in allowed


def test_db_rejects_a_non_approved_event_type(sqlite_engine):
    # SQLite enforces the CHECK: a failed/canceled billing event is impossible.
    t = UsageEvent.__table__
    with pytest.raises(IntegrityError):
        with sqlite_engine.begin() as conn:
            conn.execute(
                t.insert().values(
                    id=uuid4(), user_id=uuid4(), song_id=uuid4(),
                    event_type="separation_failed",
                )
            )


def test_no_application_code_creates_usage_events():
    # No finalizer exists in P2: no app module (outside the model definition)
    # instantiates a UsageEvent, so nothing writes usage for any job — succeeded,
    # failed or canceled. Behavioral finalizer tests are deferred to P5/P7.
    offenders = []
    for py in APP_DIR.rglob("*.py"):
        if py.name == "models.py":
            continue  # the model is *defined* here; that is not a write path
        if re.search(r"\bUsageEvent\s*\(", py.read_text(encoding="utf-8")):
            offenders.append(str(py.relative_to(APP_DIR)))
    assert offenders == [], f"unexpected UsageEvent creation in: {offenders}"


def test_no_finalizer_or_service_layer_exists():
    # DEC-0008 §8/§11: no finalizer/business-logic or service layer in P2-004.
    for name in ("services", "finalizer", "finalize", "billing", "quota"):
        assert not (APP_DIR / name).exists(), f"unexpected app/{name}"
