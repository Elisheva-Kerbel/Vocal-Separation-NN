"""Local-only benchmark CLI — Phase 1 (TASK-P1-003).

Runs the AI separation *benchmark harness* against a local audio file, writing
Vocals + Background outputs and a metrics JSON. It is a developer/benchmark tool
only: it connects to NOTHING (no upload API, DB, queue, Redis or S3/MinIO) and
loads/downloads NO model. Real inference and audio I/O are still boundary
placeholders (arriving in P1-004+), so the current real path fails *safely* and
writes a metrics JSON with ``success=false`` instead of crashing with a raw
traceback.

Input contract (logical only):

- ``--input``       local benchmark audio file path (server-side, local file).
- ``--output-dir``  local directory for outputs + metrics JSON.
- ``--model-tier``  logical tier, exactly ``Basic`` or ``Professional``.

The CLI accepts NO checkpoint path/filename/id, storage key, URL or S3/MinIO
path — checkpoint selection stays server-side. ``checkpoint_registry`` maps the
logical tier to an opaque internal reference that is NEVER exposed to CLI
output, JSON, stdout/stderr or errors. Only Vocals + Background are ever produced
(02-product-scope-and-do-not-build).

Usage (run inside the backend container, WORKDIR /app)::

    python scripts/run_benchmark.py --input PATH --output-dir DIR --model-tier Basic
"""

from __future__ import annotations

import argparse
import os
import sys
import time

# Allow running as a plain script (``python scripts/run_benchmark.py``): make the
# backend root importable so the first-party ``ai`` package resolves regardless
# of how the script is invoked. No third-party path manipulation, no network.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai import audio_io, checkpoint_registry, inference  # noqa: E402
from ai.metrics import BenchmarkMetrics, write_metrics  # noqa: E402
from ai.model import ModelTier, Stem  # noqa: E402

# Safe, fixed failure reason codes. Each is a short constant — never derived from
# an exception message, an echoed argument, a path or any secret — so metrics and
# CLI output cannot leak. The "<step>_not_implemented" reasons are built only from
# the controlled step names below.
FAILURE_INVALID_MODEL_TIER = "invalid_model_tier"
FAILURE_INPUT_NOT_FOUND = "input_not_found"
FAILURE_BENCHMARK_ERROR = "benchmark_error"

# Ordered AI pipeline steps; a placeholder boundary raises NotImplementedError and
# yields "<step>_not_implemented" (e.g. "inference_not_implemented").
_STEP_DECODE = "decode"
_STEP_INFERENCE = "inference"
_STEP_ENCODE = "encode"

# Fixed local output file names for the two in-scope stems.
_OUTPUT_FILENAMES = {
    Stem.VOCALS: "vocals.wav",
    Stem.BACKGROUND: "background.wav",
}

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def _encode_stems(stems: dict, output_dir: str) -> tuple[int, int]:
    """Encode the two in-scope stems to local files and return their byte sizes.

    Writes exactly Vocals + Background (never extra stems) via the AI encode
    boundary, then measures each output's size. Called only after separation
    returns stems, so on the real (unimplemented) path no output files exist.
    """
    os.makedirs(output_dir, exist_ok=True)
    sizes: dict[Stem, int] = {}
    for stem in (Stem.VOCALS, Stem.BACKGROUND):
        destination = os.path.join(output_dir, _OUTPUT_FILENAMES[stem])
        audio_io.save_audio(stems[stem], destination)
        sizes[stem] = os.path.getsize(destination)
    return sizes[Stem.VOCALS], sizes[Stem.BACKGROUND]


def run_benchmark(input_path: str, output_dir: str, model_tier: str) -> BenchmarkMetrics:
    """Run one local benchmark and write outputs + metrics JSON.

    Returns the :class:`BenchmarkMetrics` for the run (also written to
    ``<output_dir>/metrics.json``). On the current real path the AI boundaries
    are not implemented, so this fails *safely*: it records a safe coded
    ``failure_reason`` and writes the metrics JSON rather than raising. Output
    audio files are written only when separation actually returns stems (a
    test-injected success path) — never fabricated on the real failure path.
    """
    success = False
    failure_reason: str | None = None
    model_tier_label: str | None = None
    decode_seconds: float | None = None
    inference_seconds: float | None = None
    encode_seconds: float | None = None
    vocals_bytes: int | None = None
    background_bytes: int | None = None
    step: str | None = None

    start = time.monotonic()
    try:
        # Server-side checkpoint selection. The opaque internal reference is
        # resolved to validate the tier and confirm a checkpoint is available for
        # it, then kept internal — never written to metrics, stdout/stderr or
        # errors. Only the safe logical tier label is surfaced.
        checkpoint_registry.resolve_checkpoint(model_tier)
        model_tier_label = checkpoint_registry.public_checkpoint_response(model_tier)[
            "modelTier"
        ]

        if not os.path.isfile(input_path):
            failure_reason = FAILURE_INPUT_NOT_FOUND
        else:
            step = _STEP_DECODE
            marker = time.monotonic()
            audio = audio_io.load_audio(input_path)
            decode_seconds = time.monotonic() - marker

            step = _STEP_INFERENCE
            marker = time.monotonic()
            stems = inference.separate(audio, ModelTier(model_tier_label))
            inference_seconds = time.monotonic() - marker

            step = _STEP_ENCODE
            marker = time.monotonic()
            vocals_bytes, background_bytes = _encode_stems(stems, output_dir)
            encode_seconds = time.monotonic() - marker

            success = True
    except ValueError:
        # Invalid / non-logical model tier (defence in depth; the CLI's argparse
        # normally rejects this first). The offending value is never echoed.
        failure_reason = FAILURE_INVALID_MODEL_TIER
    except NotImplementedError:
        # A still-unimplemented AI boundary (decode/inference/encode). Only a safe
        # coded reason naming the step is recorded — no traceback or message.
        failure_reason = f"{step}_not_implemented" if step else FAILURE_BENCHMARK_ERROR
    except Exception:  # noqa: BLE001 - benchmark must never crash with a raw traceback
        failure_reason = FAILURE_BENCHMARK_ERROR

    runtime_seconds = time.monotonic() - start

    metrics = BenchmarkMetrics(
        success=success,
        failure_reason=failure_reason,
        model_tier=model_tier_label,
        runtime_seconds=runtime_seconds,
        decode_seconds=decode_seconds,
        inference_seconds=inference_seconds,
        encode_seconds=encode_seconds,
        vocals_bytes=vocals_bytes,
        background_bytes=background_bytes,
        # No checkpoint/model is loaded in P1-003, so there is no cold/warm
        # checkpoint-load timing to record; these stay null (real measurement
        # arrives with real inference in P1-004).
        checkpoint_cold_start_seconds=None,
        checkpoint_warm_start_seconds=None,
    )

    try:
        write_metrics(metrics, output_dir)
    except OSError:
        # Output directory not writable: nothing can be persisted. Do not crash;
        # main() still reports the non-zero exit for the failed run.
        pass

    return metrics


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser.

    Only three logical flags exist; ``--model-tier`` is constrained to the two
    accepted tiers. Any other flag (a ``--checkpoint`` / ``--url`` / storage-key
    style argument) or a path/URL/storage value for ``--model-tier`` is rejected
    by argparse with exit code 2 before any benchmark runs.
    """
    parser = argparse.ArgumentParser(
        prog="run_benchmark",
        description=(
            "Local-only StemSpace AI benchmark: separate a local audio file into "
            "Vocals + Background and write a metrics JSON. No API/DB/queue/storage."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Local benchmark audio file (server-side local path).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        metavar="PATH",
        help="Local directory for outputs and the metrics JSON.",
    )
    parser.add_argument(
        "--model-tier",
        required=True,
        choices=[tier.value for tier in ModelTier],
        help="Logical model tier: Basic or Professional (never a checkpoint path).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Returns 0 on success, non-zero on safe failure.

    Argument errors (missing/unknown flags, an invalid tier, or any attempt to
    pass a checkpoint path/URL/storage key as an unknown flag) are rejected by
    argparse with exit code 2 before any benchmark runs. Any unexpected error is
    caught so the user never sees a raw traceback.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        metrics = run_benchmark(args.input, args.output_dir, args.model_tier)
    except Exception:  # noqa: BLE001 - never surface a raw traceback to the user
        print(f"benchmark: failed reason={FAILURE_BENCHMARK_ERROR}", file=sys.stderr)
        return EXIT_FAILURE

    # Safe one-line summary: the success flag, the logical tier and (on failure)
    # the safe reason code only. No path, checkpoint reference, storage key or
    # secret is printed.
    if metrics.success:
        print(f"benchmark: success modelTier={metrics.model_tier}")
        return EXIT_SUCCESS

    print(
        f"benchmark: failed modelTier={metrics.model_tier or 'unknown'} "
        f"reason={metrics.failure_reason}",
        file=sys.stderr,
    )
    return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
