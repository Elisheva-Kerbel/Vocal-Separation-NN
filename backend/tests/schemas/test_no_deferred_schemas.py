"""P2-003 no-deferred / no-internal-schema tests (DEC-0007 §4, §9, §11.9, §11.10).

Prove P2-003 created NO schema for the entities DEC-0007 §4 excludes (SongTag,
UsageEvent, DailyUsage, and the deferred Rating / Coupon / CouponRedemption /
SignedUrlGrant / ContentReport / AdminAuditEvent), NO internal storage-key schema
(DEC-0007 §9), and NO API route / service surface — and that the schema layer pulls
no storage / queue / AI client.
"""

import inspect
from pathlib import Path

from pydantic import BaseModel

import app.schemas as schemas_pkg
import app.schemas.common as common_mod
import app.schemas.core as core_mod

APP_DIR = Path(schemas_pkg.__file__).resolve().parents[1]  # .../app
SCHEMAS_DIR = Path(schemas_pkg.__file__).resolve().parent

APPROVED_CLASSES = {
    "UserRead",
    "SongRead",
    "AudioFileRead",
    "SeparationJobRead",
    "TagRead",
    "CommonMessage",
}

# Entities that must NOT get a schema in P2-003 (DEC-0007 §4) — checked both as the
# bare entity name and as a ``*Read`` schema name.
DEFERRED_ENTITIES = {
    "SongTag",
    "UsageEvent",
    "DailyUsage",
    "Rating",
    "Coupon",
    "CouponRedemption",
    "SignedUrlGrant",
    "ContentReport",
    "AdminAuditEvent",
}


def _defined_schema_classes():
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


def test_only_the_approved_schema_classes_are_defined():
    assert set(_defined_schema_classes()) == APPROVED_CLASSES


def test_no_schema_for_any_deferred_or_internal_entity():
    defined = set(_defined_schema_classes())
    for entity in DEFERRED_ENTITIES:
        assert entity not in defined, entity
        assert f"{entity}Read" not in defined, f"{entity}Read"


def test_no_internal_storage_key_schema_exists():
    # DEC-0007 §9: not even an "internal-only" schema may carry storage_key.
    for name, cls in _defined_schema_classes().items():
        assert "storage_key" not in cls.model_fields, name


def test_no_create_update_admin_or_internal_named_schema():
    for name in _defined_schema_classes():
        for banned in ("Create", "Update", "Admin", "Internal"):
            assert banned not in name, name


def test_no_api_route_or_service_surface_exists():
    # P2-003 adds schemas only — no routes, no service/repository layer.
    for name in ("api", "routers", "services"):
        assert not (APP_DIR / name).exists(), f"unexpected app/{name}"


def test_schema_layer_pulls_no_storage_queue_or_ai_client():
    for py in SCHEMAS_DIR.glob("*.py"):
        src = py.read_text(encoding="utf-8")
        for forbidden in (
            "redis",
            "celery",
            "boto3",
            "minio",
            "torch",
            "librosa",
            "soundfile",
        ):
            assert forbidden not in src, f"{py.name}: {forbidden}"
