"""Phase 1 (TASK-P1-001) AI module-boundary import tests.

Prove that every ``ai`` boundary module imports with only the Phase 0 backend
dependencies (no API / DB / queue / Redis / storage / AI-model libraries), that
importing them pulls in none of the forbidden heavy libraries, that the
checkpoint boundary neither accepts nor exposes a raw checkpoint path, that the
inference/audio boundaries stay non-executing placeholders, and that only the two
in-scope stems (Vocals + Background) exist.
"""

import inspect
import subprocess
import sys

import pytest

import ai
import ai.audio_io as audio_io
import ai.checkpoint_registry as checkpoint_registry
import ai.inference as inference
import ai.metrics as metrics
import ai.model as model

# Libraries P1-001 must not require or pull in: AI/audio, DB, queue, Redis and
# storage clients (matches the task's forbidden-import list).
FORBIDDEN_LIBS = [
    "torch",
    "demucs",
    "librosa",
    "soundfile",
    "numpy",
    "scipy",
    "celery",
    "redis",
    "sqlalchemy",
    "boto3",
    "minio",
]


def test_all_ai_modules_import():
    # Every required boundary module loads.
    for mod in (ai, model, inference, audio_io, metrics, checkpoint_registry):
        assert mod is not None


def test_importing_ai_pulls_no_forbidden_libs():
    # A fresh interpreter importing only the ai package must not pull in any
    # forbidden AI/DB/queue/storage library — regardless of what happens to be
    # installed on the host. This proves the boundary needs none of them.
    code = (
        "import sys\n"
        "import ai, ai.model, ai.inference, ai.audio_io, ai.metrics, "
        "ai.checkpoint_registry\n"
        f"forbidden = {FORBIDDEN_LIBS!r}\n"
        "hit = [m for m in forbidden if m in sys.modules]\n"
        "print(','.join(hit))\n"
        "sys.exit(1 if hit else 0)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, f"forbidden libs imported by ai: {result.stdout!r}"


def test_only_vocals_and_background_stems():
    # Vocals + Background are the ONLY stems; no extra stems may be introduced.
    assert {stem.value for stem in model.Stem} == {"vocals", "background"}
    assert len(model.Stem) == 2


def test_inference_is_non_executing_placeholder():
    # The inference boundary must not run anything yet.
    with pytest.raises(NotImplementedError):
        inference.separate(audio_io.AudioBuffer(), "logical-tier")


def test_inference_takes_logical_tier_not_checkpoint_path():
    # The inference flow receives a logical modelTier — never a checkpoint path.
    params = inspect.signature(inference.separate).parameters
    assert set(params) == {"audio", "model_tier"}
    for name in params:
        assert "checkpoint" not in name
        assert "path" not in name


def test_audio_io_placeholders_do_not_execute():
    # I/O boundaries exist but perform no real decode/encode yet.
    with pytest.raises(NotImplementedError):
        audio_io.load_audio("local-fixture.wav")
    with pytest.raises(NotImplementedError):
        audio_io.save_audio(audio_io.AudioBuffer(), "local-output.wav")


def test_checkpoint_boundary_takes_logical_tier_only():
    # The registry boundary accepts only a logical tier, never a raw checkpoint
    # path/filename/id parameter.
    params = inspect.signature(checkpoint_registry.resolve_checkpoint).parameters
    assert set(params) == {"model_tier"}
    for name in params:
        assert "checkpoint" not in name
        assert "path" not in name
        assert "file" not in name


@pytest.mark.parametrize(
    "raw",
    [
        "/models/vocals.pt",
        "..\\checkpoints\\model.ckpt",
        "backend/ai/checkpoints/model.safetensors",
        "C:\\models\\demucs.pth",
        "model.onnx",
        "~/secret_checkpoint.bin",
        "",
    ],
)
def test_checkpoint_boundary_rejects_raw_paths(raw):
    # A client-style caller cannot smuggle a checkpoint path/filename/id in.
    with pytest.raises(ValueError):
        checkpoint_registry.resolve_checkpoint(raw)


def test_checkpoint_boundary_rejects_unknown_logical_tier():
    # P1-002 implements the tier mapping: an unknown logical token is now a safe
    # ValueError (never a resolved path). Only Basic/Professional are accepted;
    # full registry behaviour is covered in test_checkpoint_registry.py.
    with pytest.raises(ValueError):
        checkpoint_registry.resolve_checkpoint("logical-tier")


def test_metrics_shape_defaults():
    # The metrics shape imports and defaults to a structured failure result.
    result = metrics.BenchmarkMetrics()
    assert result.success is False
    assert result.failure_reason is None
    for field in ("runtime_seconds", "inference_seconds", "vocals_bytes"):
        assert hasattr(result, field)
