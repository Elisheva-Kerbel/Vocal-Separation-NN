"""Benchmark metrics shape — Phase 1 (TASK-P1-001) placeholder only.

Names the shape of the per-run benchmark metrics the CLI will emit later. This is
a passive data shape: it collects nothing, times nothing and touches no file,
network or service. Metric collection and JSON output are implemented in the
benchmark task (P1-003).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkMetrics:
    """Shape of one benchmark run's metrics (populated later, in P1-003).

    Captures the run outcome plus the timings/sizes the phase-level acceptance
    calls for. ``success`` together with a structured ``failure_reason`` gives
    benchmark functions a minimal structured failure result without
    over-building. Every measured field defaults to ``None`` because P1-001
    defines only the shape, not the collection.
    """

    success: bool = False
    failure_reason: str | None = None
    runtime_seconds: float | None = None
    decode_seconds: float | None = None
    inference_seconds: float | None = None
    encode_seconds: float | None = None
    vocals_bytes: int | None = None
    background_bytes: int | None = None
