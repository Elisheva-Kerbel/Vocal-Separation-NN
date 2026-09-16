"""AI model vocabulary — Phase 1 model tiers and output stems.

Defines the minimal, framework-free types the benchmark harness shares: the two
output stems and the accepted, logical model tiers. No model is loaded,
downloaded or executed here, and no ML/audio library is imported — real model
handling belongs to a later Phase 1 task (P1-003).
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


class ModelTier(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
