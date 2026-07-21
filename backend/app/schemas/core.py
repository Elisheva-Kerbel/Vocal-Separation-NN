"""P2-003 read-only, client-facing core schemas (DEC-0007 §3, §5).

The external Pydantic v2 contract for the P2-002 core entities. Each schema
deliberately exposes a *safe subset* of its model's columns — the omission of a
column (e.g. ``AudioFile.storage_key``, or a table's ``updated_at``) is
intentional, not an oversight (DEC-0007 §5, §8). Together these schemas discharge
risk R-004 by proving **DB model != API schema**: no ``storage_key``, no
bucket/provider, no signed/public URL, no checkpoint/local path and no secret ever
crosses this boundary.

Read-only only — no create/update/admin/deferred-entity schema (DEC-0007 §2, §4),
no route, no service, no ORM passthrough. Fields are named explicitly and
``extra="forbid"`` closes each field set, so an unexpected private field (e.g.
``storage_key``) is rejected rather than silently passed through (DEC-0007 §6, §8).
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# extra="forbid": the read schemas are closed, explicitly-named field sets. An
# unexpected/private attribute (a storage key, a URL, a path) is a hard error, not
# a silent leak (DEC-0007 §6, §8). No implicit ORM-attribute passthrough is enabled
# either: there is no route or service consumer in P2-003, so none is added (DEC-0002).
_READ_CONFIG = ConfigDict(extra="forbid")


class UserRead(BaseModel):
    """Client-facing account view (DEC-0007 §5.1). No password/auth-credential
    field (none exists; authentication is Phase 3)."""

    model_config = _READ_CONFIG

    id: UUID
    email: str
    status: str
    created_at: datetime
    updated_at: datetime


class SongRead(BaseModel):
    """Client-facing song view (DEC-0007 §5.2). No storage reference and no
    public/visibility field — everything is private in Phase 2."""

    model_config = _READ_CONFIG

    id: UUID
    user_id: UUID
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class AudioFileRead(BaseModel):
    """The R-004 proof schema (DEC-0007 §5.3, §7). ``AudioFile`` is the sole owner
    of ``storage_key``; this schema exposes only safe audio metadata and
    deliberately excludes ``storage_key`` and every other forbidden field (§8) —
    no bucket, no provider, no signed/public URL, no local/checkpoint path.
    ``updated_at`` is intentionally not exposed."""

    model_config = _READ_CONFIG

    id: UUID
    song_id: UUID
    purpose: str
    content_type: str
    byte_size: int
    checksum_sha256: str | None
    duration_seconds: Decimal | None
    original_filename: str | None
    created_at: datetime


class SeparationJobRead(BaseModel):
    """Client-facing separation-job view (DEC-0007 §5.4). ``model_tier`` is a
    logical enum only (``basic``), never a checkpoint/model/local path.
    ``error_message`` is short, safe failure text — never a path, secret or
    ``DATABASE_URL``."""

    model_config = _READ_CONFIG

    id: UUID
    song_id: UUID
    status: str
    model_tier: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TagRead(BaseModel):
    """Client-facing tag view (DEC-0007 §5.5). ``updated_at`` is intentionally not
    exposed."""

    model_config = _READ_CONFIG

    id: UUID
    slug: str
    name: str
    created_at: datetime
