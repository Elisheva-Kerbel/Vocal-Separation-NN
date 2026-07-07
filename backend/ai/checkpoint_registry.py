"""Checkpoint registry — server-side modelTier -> internal reference (P1-002).

Checkpoint selection is **server-side only**. A client may request a *logical*
``ModelTier`` (Basic or Professional) and nothing else; it never sends — and
never receives — a checkpoint path, filename, free checkpoint id, URL or storage
key. ``resolve_checkpoint`` maps an accepted tier to an **opaque internal
reference** for backend use; ``public_checkpoint_response`` returns only the
client-safe tier label, never the internal reference.

The internal references here are deliberately opaque placeholders — P1-002 does
not choose a real model/checkpoint (that remains open decision OD-004). They are
not paths, filenames, URLs, storage keys or real checkpoint locations. No
filesystem, ``checkpoints/`` or network access happens here: nothing is read,
created, downloaded or existence-checked.
"""

from __future__ import annotations

from .model import ModelTier

# Opaque, internal-only references. NOT paths, filenames, URLs, S3/MinIO keys or
# real checkpoint locations — just safe placeholders until a real checkpoint is
# approved in a later, separate decision (OD-004). Server-side use only.
_CHECKPOINT_REGISTRY: dict[ModelTier, str] = {
    ModelTier.BASIC: "basic-placeholder",
    ModelTier.PROFESSIONAL: "professional-placeholder",
}

# Safe, client-facing wording for rejected input. Lists the accepted tiers and
# never contains an internal reference, path, storage key or secret.
_ACCEPTED = ", ".join(tier.value for tier in ModelTier)  # "Basic, Professional"
_INVALID_TIER_MESSAGE = f"Invalid model tier. Accepted tiers: {_ACCEPTED}."
_NOT_A_TIER_MESSAGE = (
    "Model tier must be a logical tier name, not a path, filename, URL or "
    f"storage key. Accepted tiers: {_ACCEPTED}."
)

# Markers that reveal a caller is passing a checkpoint *path*, filename, URL or
# storage key (e.g. C:\\, http://, s3://) instead of a logical tier name. The
# ":" marker covers Windows drives and URL/storage schemes at once.
_PATH_MARKERS = ("/", "\\", "..", "~", ":")
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


def _reject_pathlike(value: str) -> None:
    """Reject a string that resembles a checkpoint path/filename/URL/storage key.

    Client-safety guard (AGENT.md: "client never sends checkpoint path, filename
    or free checkpoint id"). Raises a safe ``ValueError`` that carries no internal
    reference, echoed input, path or secret.
    """
    if any(marker in value for marker in _PATH_MARKERS):
        raise ValueError(_NOT_A_TIER_MESSAGE)
    if value.strip().lower().endswith(_CHECKPOINT_SUFFIXES):
        raise ValueError(_NOT_A_TIER_MESSAGE)


def _coerce_tier(model_tier: ModelTier | str) -> ModelTier:
    """Validate arbitrary input down to an accepted :class:`ModelTier`.

    Accepts a :class:`ModelTier` member or the exact string ``"Basic"`` /
    ``"Professional"``. Everything else — non-strings, empty strings, path / URL /
    filename-like values and any other free-form checkpoint id or tier name — is
    rejected with a safe ``ValueError``. No normalization (case/whitespace) is
    applied: matching is exact.
    """
    if isinstance(model_tier, ModelTier):
        return model_tier
    if not isinstance(model_tier, str):
        raise ValueError(_INVALID_TIER_MESSAGE)
    _reject_pathlike(model_tier)
    try:
        return ModelTier(model_tier)
    except ValueError:
        raise ValueError(_INVALID_TIER_MESSAGE) from None


def resolve_checkpoint(model_tier: ModelTier | str) -> str:
    """Map an accepted ``model_tier`` to its opaque internal reference.

    **Server-side / internal use only.** Returns an opaque placeholder reference
    (never a path, filename, URL or storage key). Invalid tiers raise a safe
    ``ValueError``. Do not return this value to a client — use
    :func:`public_checkpoint_response` for client-facing output.
    """
    return _CHECKPOINT_REGISTRY[_coerce_tier(model_tier)]


def public_checkpoint_response(model_tier: ModelTier | str) -> dict[str, str]:
    """Client-safe view for an accepted ``model_tier``.

    Echoes only the validated logical tier label — never the internal reference,
    a path, storage key, URL or checkpoint filename. Invalid tiers raise the same
    safe ``ValueError`` as :func:`resolve_checkpoint`.
    """
    return {"modelTier": _coerce_tier(model_tier).value}
