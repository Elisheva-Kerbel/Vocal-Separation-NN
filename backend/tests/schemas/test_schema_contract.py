"""P2-003 schema-contract tests (DEC-0007 §11.1-§11.3, §11.8).

Prove the schema layer is EXACTLY the DEC-0007 contract: only the six approved
read-only classes exist, each class's ``model_fields`` equals its DEC-0007 §5 field
list, Pydantic v2 idioms are used (and v1 idioms are not), ``model_dump()`` works,
and no create/update (or any other) schema class was introduced. Assertions inspect
actual ``model_fields`` (Pydantic v2), not only hardcoded denylist strings.
"""

import inspect
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel

import app.schemas as schemas_pkg
import app.schemas.common as common_mod
import app.schemas.core as core_mod
from app.schemas import (
    AudioFileRead,
    CommonMessage,
    SeparationJobRead,
    SongRead,
    TagRead,
    UserRead,
)

SCHEMAS_DIR = Path(schemas_pkg.__file__).resolve().parent

APPROVED_CLASSES = {
    "UserRead",
    "SongRead",
    "AudioFileRead",
    "SeparationJobRead",
    "TagRead",
    "CommonMessage",
}

# DEC-0007 §5 — the exact, closed field set per class.
EXPECTED_FIELDS = {
    UserRead: {"id", "email", "status", "created_at", "updated_at"},
    SongRead: {"id", "user_id", "title", "status", "created_at", "updated_at"},
    AudioFileRead: {
        "id",
        "song_id",
        "purpose",
        "content_type",
        "byte_size",
        "checksum_sha256",
        "duration_seconds",
        "original_filename",
        "created_at",
    },
    SeparationJobRead: {
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
    TagRead: {"id", "slug", "name", "created_at"},
    CommonMessage: {"message"},
}


def _defined_schema_classes():
    """All BaseModel subclasses DEFINED in the schema modules (not re-imports)."""
    found = {}
    for module in (common_mod, core_mod):
        for name, obj in vars(module).items():
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseModel)
                and obj is not BaseModel
                and obj.__module__ == module.__name__
            ):
                found[name] = obj
    return found


def _sample(cls):
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    data = {
        UserRead: dict(
            id=uuid4(),
            email="user@example.com",
            status="active",
            created_at=now,
            updated_at=now,
        ),
        SongRead: dict(
            id=uuid4(),
            user_id=uuid4(),
            title="My Song",
            status="uploaded",
            created_at=now,
            updated_at=now,
        ),
        AudioFileRead: dict(
            id=uuid4(),
            song_id=uuid4(),
            purpose="original",
            content_type="audio/wav",
            byte_size=1234,
            checksum_sha256="a" * 64,
            duration_seconds=Decimal("123.45"),
            original_filename="track.wav",
            created_at=now,
        ),
        SeparationJobRead: dict(
            id=uuid4(),
            song_id=uuid4(),
            status="queued",
            model_tier="basic",
            error_message=None,
            started_at=None,
            finished_at=None,
            created_at=now,
            updated_at=now,
        ),
        TagRead: dict(id=uuid4(), slug="vocals", name="Vocals", created_at=now),
        CommonMessage: dict(message="ok"),
    }
    return cls(**data[cls])


def test_exactly_the_six_approved_schema_classes_exist():
    assert set(_defined_schema_classes()) == APPROVED_CLASSES


def test_public_package_exports_exactly_the_approved_classes():
    exported = {
        name
        for name, obj in vars(schemas_pkg).items()
        if inspect.isclass(obj) and issubclass(obj, BaseModel)
    }
    assert exported == APPROVED_CLASSES
    assert set(schemas_pkg.__all__) == APPROVED_CLASSES


def test_each_schema_has_exact_dec0007_field_set():
    for cls, expected in EXPECTED_FIELDS.items():
        assert set(cls.model_fields) == expected, cls.__name__


def test_schemas_use_pydantic_v2_config_idiom():
    for cls in EXPECTED_FIELDS:
        # v2 exposes config as a dict; extra="forbid" closes the field set.
        assert isinstance(cls.model_config, dict)
        assert cls.model_config.get("extra") == "forbid", cls.__name__


def test_schema_source_uses_no_pydantic_v1_idioms():
    for py in SCHEMAS_DIR.glob("*.py"):
        src = py.read_text(encoding="utf-8")
        for v1 in ("orm_mode", "__fields__", ".dict(", "from_orm"):
            assert v1 not in src, f"{py.name}: {v1}"


def test_model_dump_serializes_exactly_the_declared_fields():
    for cls, expected in EXPECTED_FIELDS.items():
        dumped = _sample(cls).model_dump()
        assert set(dumped) == expected, cls.__name__


def test_no_create_update_or_admin_schema_classes_exist():
    for name in _defined_schema_classes():
        assert not name.endswith("Create"), name
        assert not name.endswith("Update"), name
        assert "Admin" not in name, name
