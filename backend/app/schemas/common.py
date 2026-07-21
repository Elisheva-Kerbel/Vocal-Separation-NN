"""P2-003 common client-facing schema (DEC-0007 §5.6).

A minimal message wrapper only. Deliberately **not** a pagination envelope, an
error/problem-details envelope or a metadata envelope (DEC-0007 §5.6, §12) — those
arrive only with the later phase that actually needs them (DEC-0002).
"""

from pydantic import BaseModel, ConfigDict


class CommonMessage(BaseModel):
    """A single human-readable message — nothing more (DEC-0007 §5.6)."""

    model_config = ConfigDict(extra="forbid")

    message: str
