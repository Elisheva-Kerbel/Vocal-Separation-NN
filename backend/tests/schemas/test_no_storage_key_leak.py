"""P2-003 storage-key / forbidden-field leak tests (DEC-0007 §7, §8, §11.4-§11.7).

The R-004 proof. Prove that no P2-003 schema exposes ``storage_key`` or any other
DEC-0007 §8 forbidden field — in its field set OR its serialized output — and that
``AudioFileRead`` (the schema for the sole owner-entity of ``storage_key``) exposes
only safe audio metadata. Assertions inspect actual ``model_fields`` and real
``model_dump()`` output, not only hardcoded denylist strings.
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import (
    AudioFileRead,
    CommonMessage,
    SeparationJobRead,
    SongRead,
    TagRead,
    UserRead,
)

ALL_SCHEMAS = (
    UserRead,
    SongRead,
    AudioFileRead,
    SeparationJobRead,
    TagRead,
    CommonMessage,
)

# DEC-0007 §8 — binding on every P2-003 schema.
FORBIDDEN_FIELDS = {
    "storage_key",
    "checkpoint_path",
    "model_path",
    "local_model_root",
    "LOCAL_MODEL_ROOT",
    "local_path",
    "path",
    "signed_url",
    "public_url",
    "url",
    "bucket",
    "provider",
    "database_url",
    "password",
    "secret",
    "token",
    "audio_bytes",
    "base64_audio",
    "binary_audio",
    "traceback",
    "internal_error",
}

# Substrings that must never appear inside any field name — catches aliases such as
# ``*_storage_key``, ``signed_url_expiry`` or ``model_checkpoint_path``. ("model" is
# intentionally NOT here: ``model_tier`` is an approved logical-enum field, §5.4.)
FORBIDDEN_SUBSTRINGS = (
    "storage",
    "checkpoint",
    "path",
    "url",
    "bucket",
    "provider",
    "secret",
    "token",
    "password",
    "traceback",
    "base64",
)

# DEC-0007 §5.3 — AudioFileRead's exact safe-metadata field set.
AUDIOFILE_SAFE_FIELDS = {
    "id",
    "song_id",
    "purpose",
    "content_type",
    "byte_size",
    "checksum_sha256",
    "duration_seconds",
    "original_filename",
    "created_at",
}


def _sample(cls):
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    data = {
        UserRead: dict(
            id=uuid4(),
            email="u@example.com",
            status="active",
            created_at=now,
            updated_at=now,
        ),
        SongRead: dict(
            id=uuid4(),
            user_id=uuid4(),
            title="t",
            status="uploaded",
            created_at=now,
            updated_at=now,
        ),
        AudioFileRead: dict(
            id=uuid4(),
            song_id=uuid4(),
            purpose="original",
            content_type="audio/wav",
            byte_size=10,
            checksum_sha256="a" * 64,
            duration_seconds=Decimal("1.0"),
            original_filename="a.wav",
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
        TagRead: dict(id=uuid4(), slug="s", name="n", created_at=now),
        CommonMessage: dict(message="ok"),
    }
    return cls(**data[cls])


def test_storage_key_absent_from_every_field_set():
    for cls in ALL_SCHEMAS:
        assert "storage_key" not in cls.model_fields, cls.__name__


def test_storage_key_absent_from_every_serialized_output():
    for cls in ALL_SCHEMAS:
        assert "storage_key" not in _sample(cls).model_dump(), cls.__name__


def test_all_forbidden_fields_absent_from_field_sets():
    for cls in ALL_SCHEMAS:
        leaked = FORBIDDEN_FIELDS & set(cls.model_fields)
        assert not leaked, f"{cls.__name__}: {leaked}"


def test_no_field_name_contains_a_forbidden_substring():
    for cls in ALL_SCHEMAS:
        for field in cls.model_fields:
            lowered = field.lower()
            for bad in FORBIDDEN_SUBSTRINGS:
                assert bad not in lowered, f"{cls.__name__}.{field}"


def test_all_forbidden_fields_absent_from_serialized_output():
    for cls in ALL_SCHEMAS:
        dumped_keys = set(_sample(cls).model_dump())
        leaked = FORBIDDEN_FIELDS & dumped_keys
        assert not leaked, f"{cls.__name__}: {leaked}"


def test_audiofile_read_exposes_only_safe_metadata():
    assert set(AudioFileRead.model_fields) == AUDIOFILE_SAFE_FIELDS
    dumped = _sample(AudioFileRead).model_dump()
    assert set(dumped) == AUDIOFILE_SAFE_FIELDS
    for forbidden in FORBIDDEN_FIELDS:
        assert forbidden not in dumped


def test_audiofile_read_rejects_a_smuggled_storage_key():
    # extra="forbid" makes attaching storage_key a hard error, not a silent leak.
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        AudioFileRead(
            id=uuid4(),
            song_id=uuid4(),
            purpose="original",
            content_type="audio/wav",
            byte_size=10,
            checksum_sha256=None,
            duration_seconds=None,
            original_filename=None,
            created_at=now,
            storage_key="s3://bucket/private-object-key",
        )
