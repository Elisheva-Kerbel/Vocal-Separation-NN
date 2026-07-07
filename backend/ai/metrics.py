"""Benchmark metrics — shape, JSON contract and writer (P1-003).

Extends the P1-001 metrics *shape* with the logical model tier and the
checkpoint cold/warm-start fields, and adds the stable JSON contract plus the
writer the benchmark CLI (``scripts/run_benchmark.py``) uses. This module stays
passive: it collects nothing and touches no model, audio, network, DB, queue,
Redis or S3/MinIO — the CLI populates a :class:`BenchmarkMetrics` and calls
:func:`write_metrics`.

The JSON contract deliberately carries only safe, non-identifying values: the run
outcome, a safe ``failure_reason`` code, the logical model tier label, timings
and output byte sizes. It never includes an internal checkpoint reference, a
filesystem path, a storage key, a URL, a secret or a traceback
(06-security-permissions-and-secrets). Only the two in-scope stems
(Vocals + Background) ever appear (02-product-scope-and-do-not-build).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

# Fixed name of the per-run metrics file written into the output directory.
METRICS_FILENAME = "metrics.json"


@dataclass(frozen=True)
class BenchmarkMetrics:
    """Shape of one benchmark run's metrics.

    ``success`` plus a safe, coded ``failure_reason`` give a minimal structured
    outcome. Every measured timing/size defaults to ``None`` because a field is
    populated only when its step actually runs — on the current real path the AI
    boundaries are not implemented yet, so most stay ``None``. The
    ``checkpoint_*_start_seconds`` fields are reserved for real checkpoint-load
    timing (P1-004+) and stay ``None`` while no checkpoint/model is loaded.
    """

    success: bool = False
    failure_reason: str | None = None
    model_tier: str | None = None
    runtime_seconds: float | None = None
    decode_seconds: float | None = None
    inference_seconds: float | None = None
    encode_seconds: float | None = None
    vocals_bytes: int | None = None
    background_bytes: int | None = None
    checkpoint_cold_start_seconds: float | None = None
    checkpoint_warm_start_seconds: float | None = None

    def to_dict(self) -> dict:
        """Serialise to the stable benchmark JSON contract.

        Keys are the phase-level required metric names; ``output_sizes`` nests
        the two in-scope stem sizes. Any timing/size may be ``null`` (or ``0``)
        when its step did not run. Carries no checkpoint ref, path, storage key,
        URL or secret.
        """
        return {
            "success": self.success,
            "failure_reason": self.failure_reason,
            "modelTier": self.model_tier,
            "total_runtime": self.runtime_seconds,
            "decode_time": self.decode_seconds,
            "inference_time": self.inference_seconds,
            "encode_time": self.encode_seconds,
            "output_sizes": {
                "vocals": self.vocals_bytes,
                "background": self.background_bytes,
            },
            "checkpoint_cold_start": self.checkpoint_cold_start_seconds,
            "checkpoint_warm_start": self.checkpoint_warm_start_seconds,
        }


def write_metrics(metrics: BenchmarkMetrics, output_dir: str) -> str:
    """Write ``metrics`` as JSON into ``output_dir`` and return the file path.

    The directory is created if missing so metrics can always be written on both
    the success and the safe-failure paths. Only the safe JSON contract from
    :meth:`BenchmarkMetrics.to_dict` is written — never a checkpoint ref, path,
    storage key, URL or secret.
    """
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, METRICS_FILENAME)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(metrics.to_dict(), handle, indent=2, sort_keys=True)
    return path
