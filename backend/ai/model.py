"""AI model vocabulary — Phase 1 (TASK-P1-001) boundaries only.

Defines the minimal, framework-free types the benchmark harness shares: the two
output stems and the *logical* model tier. No model is loaded, downloaded or
executed here, and no ML/audio library is imported — real model handling belongs
to the later Phase 1 tasks (P1-002 / P1-003).
"""

from __future__ import annotations

from enum import Enum


class Stem(str, Enum):
    """The only two output stems in scope for the whole project.

    Vocals + Background only. Extra stems are explicitly out of scope and must
    not be added (02-product-scope-and-do-not-build).
    """

    VOCALS = "vocals"
    BACKGROUND = "background"


# Logical, client-safe selector for the inference flow. A ``ModelTier`` is an
# opaque logical token (e.g. a tier name); it is NEVER a checkpoint path,
# filename or free checkpoint id. Mapping a tier to an actual checkpoint is a
# server-side concern handled by ``checkpoint_registry`` in a later task
# (P1-002). Kept as a plain string alias so P1-001 does not fix the tier
# vocabulary yet.
ModelTier = str
