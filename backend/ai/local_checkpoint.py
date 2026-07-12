"""Local prototype checkpoint resolution (P1-004B) — server-side only.

Resolves the **local, out-of-band** checkpoint that the Basic local prototype
adapter will load *later* (real load is P1-004C). This module:

- reads the local model folder **only** from the ``LOCAL_MODEL_ROOT`` environment
  variable (operator-provided, never committed — see DEC-0004);
- picks the checkpoint **filename** from an internal boolean selector
  (``use_best_model``), never from any caller / CLI / client input;
- **never** loads a checkpoint, imports torch, or touches the network;
- **never** exposes the resolved local path in return-to-caller strings, CLI
  output, metrics, logs or exception messages (safe, fixed error text only).

Stdlib only — importing this module pulls in no heavy AI/audio library, so the AI
boundary stays import-light (see ``tests/ai/test_imports.py``).
"""

from __future__ import annotations

import os
from pathlib import Path

# Operator-provided environment variables (local prototype only, DEC-0004).
ENV_MODEL_ROOT = "LOCAL_MODEL_ROOT"
ENV_USE_BEST = "LOCAL_MODEL_USE_BEST"

# Sub-directory (under the local model root) that holds the checkpoint files,
# matching the inspected local reference layout ``<root>/checkpoints/<file>``.
_CHECKPOINTS_SUBDIR = "checkpoints"

# Internal, fixed checkpoint filenames. These are the ONLY names ever used; they
# are never derived from a caller/CLI/client argument.
BEST_MODEL_FILENAME = "best_model.pt"

# TEMPORARY local-prototype behavior (DEC-0004 §5): no separate "basic" checkpoint
# exists yet, so the basic slot currently *reuses* best_model.pt. This is a
# prototype convenience ONLY. It is NOT a real Professional tier and NOT a second
# trained model; ``use_best_model=false`` must not be presented as Professional.
# When a distinct basic checkpoint is approved later, only this constant changes.
BASIC_SLOT_FILENAME = BEST_MODEL_FILENAME
BASIC_SLOT_IS_TEMPORARY_ALIAS = BASIC_SLOT_FILENAME == BEST_MODEL_FILENAME


class LocalModelError(RuntimeError):
    """Base for safe local-model errors. Messages never contain the local path."""


class LocalModelConfigError(LocalModelError):
    """``LOCAL_MODEL_ROOT`` is missing/empty. Safe message, no path."""


class LocalCheckpointNotFoundError(LocalModelError):
    """The internal checkpoint file is absent under the configured root. No path."""


# Fixed, safe error text — deliberately free of any path, filename or secret.
_MISSING_ROOT_MESSAGE = (
    "Local model root is not configured. Set the LOCAL_MODEL_ROOT environment "
    "variable to your local, out-of-band model folder (never committed)."
)
_CHECKPOINT_MISSING_MESSAGE = (
    "Local checkpoint is not available under the configured local model root."
)


def checkpoint_filename(use_best_model: bool) -> str:
    """Map the internal boolean selector to a checkpoint filename.

    ``use_best_model=True``  -> ``best_model.pt``.
    ``use_best_model=False`` -> the basic checkpoint slot (temporarily the same
    file, see :data:`BASIC_SLOT_FILENAME`).

    Only a ``bool`` is accepted: a path / filename / URL / storage-key string is
    rejected with ``TypeError`` and is never treated as a checkpoint name. This
    keeps checkpoint naming server-side and prevents smuggling a path in.
    """
    if not isinstance(use_best_model, bool):
        raise TypeError("use_best_model must be a bool (never a path/filename/id).")
    return BEST_MODEL_FILENAME if use_best_model else BASIC_SLOT_FILENAME


def _model_root() -> Path:
    """Read ``LOCAL_MODEL_ROOT`` or fail safely (no path in the error)."""
    raw = os.environ.get(ENV_MODEL_ROOT)
    if raw is None or raw.strip() == "":
        raise LocalModelConfigError(_MISSING_ROOT_MESSAGE)
    return Path(raw.strip())


def use_best_model_from_env(default: bool = True) -> bool:
    """Read the optional ``LOCAL_MODEL_USE_BEST`` selector (local benchmark only).

    Absent -> ``default``. Truthy tokens (``1/true/yes/on``, case-insensitive)
    select the best model; anything else selects the basic slot. This never
    accepts or returns a path/filename.
    """
    raw = os.environ.get(ENV_USE_BEST)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def resolve_checkpoint_path(use_best_model: bool, *, require_exists: bool = True) -> Path:
    """Resolve the internal local checkpoint path. **Server-side / internal only.**

    The filename comes solely from the boolean ``use_best_model`` selector (never
    from a caller-supplied path/filename/URL/storage key). The returned ``Path``
    is for internal backend use by the adapter — it must never be surfaced to the
    CLI, metrics, logs or exception messages. When ``require_exists`` and the file
    is absent, a safe :class:`LocalCheckpointNotFoundError` is raised whose message
    contains no path. No checkpoint is loaded and no torch import happens here.
    """
    path = _model_root() / _CHECKPOINTS_SUBDIR / checkpoint_filename(use_best_model)
    if require_exists and not path.is_file():
        raise LocalCheckpointNotFoundError(_CHECKPOINT_MISSING_MESSAGE)
    return path
