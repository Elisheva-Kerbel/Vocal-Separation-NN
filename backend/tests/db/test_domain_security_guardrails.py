"""P2-002 security-guardrail tests (DEC-0006 §5–§7).

Permanent regression guards proving the data model stores no audio bytes, no
checkpoint/model/local filesystem paths, no signed-URL strings and no public URLs;
that ``storage_key`` lives only on ``AudioFile``; that ``model_tier`` is a logical
enum; and that P2-002 created no API/schema/service surface. Metadata + filesystem
inspection only — no engine, no connection.
"""

from pathlib import Path

from sqlalchemy import LargeBinary

from app.db import models  # noqa: F401  ensures the tables are registered
from app.db.base import Base

APP_DIR = Path(__file__).resolve().parents[2] / "app"
MODELS_PY = APP_DIR / "db" / "models.py"

FORBIDDEN_PATH_NAMES = {
    "checkpoint_path",
    "model_path",
    "local_model_root",
    "local_path",
    "path",
    "file_path",
    "use_best_model",
}
FORBIDDEN_AUDIO_NAMES = {
    "audio_bytes",
    "audio_blob",
    "binary_audio",
    "audio_base64",
    "audio_data",
    "blob",
}


def _all_columns():
    for table in Base.metadata.tables.values():
        for column in table.columns:
            yield table.name, column


def test_no_large_binary_or_bytea_columns():
    for table_name, column in _all_columns():
        assert not isinstance(column.type, LargeBinary), f"{table_name}.{column.name}"
        type_text = str(column.type).upper()
        assert "BYTEA" not in type_text
        assert "BLOB" not in type_text


def test_no_path_columns():
    for table_name, column in _all_columns():
        lowered = column.name.lower()
        assert lowered not in FORBIDDEN_PATH_NAMES, f"{table_name}.{column.name}"
        assert "path" not in lowered, f"{table_name}.{column.name}"


def test_no_checkpoint_or_model_root_columns():
    for _table_name, column in _all_columns():
        lowered = column.name.lower()
        assert "checkpoint" not in lowered
        assert "local_model_root" not in lowered
        assert "model_root" not in lowered


def test_no_signed_url_or_public_url_columns():
    for table_name, column in _all_columns():
        lowered = column.name.lower()
        assert "url" not in lowered, f"{table_name}.{column.name}"
        assert "signed" not in lowered
        assert "public" not in lowered


def test_no_audio_bytes_columns():
    for table_name, column in _all_columns():
        assert (
            column.name.lower() not in FORBIDDEN_AUDIO_NAMES
        ), f"{table_name}.{column.name}"


def test_storage_key_exists_only_on_audio_files():
    owners = {
        table.name
        for table in Base.metadata.tables.values()
        if "storage_key" in table.columns
    }
    assert owners == {"audio_files"}


def test_model_tier_is_logical_string_enum_not_a_path():
    column = Base.metadata.tables["separation_jobs"].c["model_tier"]
    assert column.type.python_type is str
    lowered = column.name.lower()
    assert "path" not in lowered and "checkpoint" not in lowered


def test_no_api_schema_or_service_surface_created():
    # P2-002 adds no API routes, no client schemas, no service/repository layer.
    for name in ("api", "routers", "schemas", "services", "models"):
        assert not (APP_DIR / name).exists(), f"unexpected app/{name}"


def test_models_module_imports_no_forbidden_clients():
    source = MODELS_PY.read_text(encoding="utf-8")
    for forbidden in ("redis", "celery", "boto3", "minio"):
        assert forbidden not in source, f"forbidden reference: {forbidden}"
