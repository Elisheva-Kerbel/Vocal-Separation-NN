"""P2-003 read-only Pydantic v2 schema layer (DEC-0007).

Exactly the six approved client-facing read schemas — no create/update/admin or
deferred-entity schema, no route, no service (DEC-0007 §2-§4). This package is the
external API contract that proves **DB model != API schema** and that private
storage state (``storage_key``, URLs, paths, secrets) never crosses the boundary
(R-004). It re-exports only the approved classes as its public surface.
"""

from app.schemas.common import CommonMessage
from app.schemas.core import (
    AudioFileRead,
    SeparationJobRead,
    SongRead,
    TagRead,
    UserRead,
)

__all__ = [
    "AudioFileRead",
    "CommonMessage",
    "SeparationJobRead",
    "SongRead",
    "TagRead",
    "UserRead",
]
