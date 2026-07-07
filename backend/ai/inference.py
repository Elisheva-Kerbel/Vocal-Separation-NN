"""Separation inference boundary — Phase 1 (TASK-P1-001) placeholder only.

Declares the single inference entry point the harness will use. It does NOT run a
model, does NOT process audio and connects to NOTHING (no network, DB, queue,
Redis or storage). Real separation is implemented in a later Phase 1 task
(P1-002 / P1-003); until then the boundary raises ``NotImplementedError``.

The flow takes a *logical* ``model_tier`` (see :data:`ai.model.ModelTier`); the
client never supplies a checkpoint path — the tier is mapped to a checkpoint
server-side via ``checkpoint_registry``. Output is exactly the two
:class:`ai.model.Stem` values, never extra stems.
"""

from __future__ import annotations

from .audio_io import AudioBuffer
from .model import ModelTier, Stem


def separate(audio: AudioBuffer, model_tier: ModelTier) -> dict[Stem, AudioBuffer]:
    """Separate ``audio`` into Vocals + Background for the given logical tier.

    Boundary/placeholder only: it raises ``NotImplementedError`` — no model is
    loaded or run, no audio is processed and nothing is connected. The real
    implementation (P1-002 / P1-003) resolves ``model_tier`` to a checkpoint
    *server-side* via ``checkpoint_registry`` (the client never supplies a
    checkpoint path) and returns exactly the two :class:`ai.model.Stem` outputs.
    """
    raise NotImplementedError(
        "Real separation inference is implemented in a later Phase 1 task "
        "(P1-002 / P1-003)."
    )
