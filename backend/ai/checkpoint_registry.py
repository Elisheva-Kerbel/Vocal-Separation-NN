"""Checkpoint registry boundary — Phase 1 (TASK-P1-001) safe boundary only.

Checkpoint selection is **server-side only**. This boundary accepts a *logical*
``model_tier`` and NEVER a checkpoint path, filename or free checkpoint id from a
client-style caller, and it never exposes an internal checkpoint path. The actual
tier -> checkpoint mapping (and any path resolution) is deliberately deferred to
the approved next task (P1-002); until then the resolver raises
``NotImplementedError`` after rejecting any client-supplied path-like input.

No filesystem, ``checkpoints/`` or network access happens here.
"""

from __future__ import annotations

from typing import NoReturn

from .model import ModelTier

# Markers that reveal a caller is trying to pass a raw checkpoint *path*,
# filename or id instead of a logical tier. Used only to REJECT such input at
# this boundary — never to resolve anything.
_PATH_MARKERS = ("/", "\\", "..", "~")
_CHECKPOINT_SUFFIXES = (
    ".pt",
    ".pth",
    ".ckpt",
    ".onnx",
    ".bin",
    ".safetensors",
    ".tar",
    ".gz",
)


def _reject_client_checkpoint_path(model_tier: ModelTier) -> None:
    """Guard: reject anything that looks like a raw checkpoint path/filename/id.

    Enforces that only a logical tier token may cross this boundary (AGENT.md:
    "client never sends checkpoint path, filename or free checkpoint id"). Raises
    ``ValueError`` on anything path-like; returns ``None`` for a plausible
    logical token (which the caller then defers to P1-002).
    """
    if not isinstance(model_tier, str) or not model_tier.strip():
        raise ValueError("model_tier must be a non-empty logical tier token.")
    if any(marker in model_tier for marker in _PATH_MARKERS):
        raise ValueError("model_tier must be a logical tier, not a path or id.")
    if len(model_tier) >= 2 and model_tier[1] == ":":  # Windows drive, e.g. C:\
        raise ValueError("model_tier must be a logical tier, not a path or id.")
    if model_tier.strip().lower().endswith(_CHECKPOINT_SUFFIXES):
        raise ValueError("model_tier must be a logical tier, not a checkpoint file.")


def resolve_checkpoint(model_tier: ModelTier) -> NoReturn:
    """Map a logical ``model_tier`` to a checkpoint — server-side only.

    P1-001 provides only the *boundary*: it rejects any client-supplied
    checkpoint path/filename/id, then raises ``NotImplementedError`` because the
    tier -> checkpoint mapping is defined in the approved next task (P1-002). It
    accepts only a logical tier and returns no path, so no internal checkpoint
    path is ever accepted from — or exposed to — a client-style caller. P1-002
    will return an opaque server-side handle, still not a raw path.
    """
    _reject_client_checkpoint_path(model_tier)
    raise NotImplementedError(
        "Checkpoint tier mapping is defined server-side in Phase 1 task P1-002."
    )
