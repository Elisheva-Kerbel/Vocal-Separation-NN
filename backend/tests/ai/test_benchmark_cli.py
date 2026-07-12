"""P1-003 benchmark CLI tests.

Prove the local-only benchmark CLI contract without real AI, audio, model or
external service:

- accepts exactly the Basic/Professional logical tiers;
- rejects invalid tiers and any checkpoint/path/URL/storage-like argument safely
  (argparse exit code 2), before any benchmark runs;
- on the real (unimplemented) path writes a metrics JSON with ``success=false``
  and a safe coded ``failure_reason``, and returns a non-zero exit;
- never leaks an internal checkpoint reference, path, storage key, URL, secret or
  traceback into the metrics JSON or stdout/stderr;
- via injected fakes (monkeypatch) drives a simulated success path that produces
  vocals/background outputs and a complete metrics JSON, returning exit 0.

Fakes are wired at the AI boundary functions only — no real audio dependency, no
model load, no downloads and no external services.
"""

import json
from pathlib import Path

import pytest

import scripts.run_benchmark as cli
from ai import audio_io, inference
from ai.model import Stem

# The internal checkpoint references from P1-002 that must never surface, plus
# generic path / URL / storage / secret / traceback markers.
_LEAK_MARKERS = (
    "basic-placeholder",
    "professional-placeholder",
    "placeholder",
    "traceback",
    "s3://",
    "minio",
    "http",
    ".pt",
    ".pth",
    ".ckpt",
    ".safetensors",
    "secret",
)

# The full set of safe failure-reason codes the CLI may emit.
_SAFE_FAILURE_REASONS = {
    "invalid_model_tier",
    "input_not_found",
    "benchmark_error",
    "decode_not_implemented",
    "inference_not_implemented",
    "encode_not_implemented",
}

_FAKE_OUTPUT_BYTES = b"FAKE-BENCHMARK-OUTPUT"


def _string_values(obj):
    if isinstance(obj, dict):
        for value in obj.values():
            yield from _string_values(value)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            yield from _string_values(value)
    elif isinstance(obj, str):
        yield obj


def _inject_fake_success(monkeypatch):
    """Wire fakes at the AI boundaries so separation 'succeeds' with no real AI."""
    monkeypatch.setattr(audio_io, "load_audio", lambda source: audio_io.AudioBuffer())

    def _fake_separate(audio, model_tier):
        return {
            Stem.VOCALS: audio_io.AudioBuffer(),
            Stem.BACKGROUND: audio_io.AudioBuffer(),
        }

    monkeypatch.setattr(inference, "separate", _fake_separate)

    def _fake_save(buffer, destination):
        with open(destination, "wb") as handle:
            handle.write(_FAKE_OUTPUT_BYTES)

    monkeypatch.setattr(audio_io, "save_audio", _fake_save)


def _existing_input(tmp_path) -> Path:
    # A non-audio placeholder file: it exists so os.path.isfile passes, but it is
    # never really decoded (decode is a placeholder / injected fake).
    path = tmp_path / "input.wav"
    path.write_bytes(b"not-real-audio")
    return path


# --- argument validation -------------------------------------------------------


@pytest.mark.parametrize("tier", ["Basic", "Professional"])
def test_accepts_valid_tiers_via_simulated_success(tier, tmp_path, monkeypatch):
    # CLI accepts Basic and Professional; the simulated success path returns 0
    # and produces vocals/background outputs + a success metrics JSON.
    _inject_fake_success(monkeypatch)
    out = tmp_path / "out"
    code = cli.main(
        [
            "--input",
            str(_existing_input(tmp_path)),
            "--output-dir",
            str(out),
            "--model-tier",
            tier,
        ]
    )
    assert code == cli.EXIT_SUCCESS
    assert (out / "vocals.wav").is_file()
    assert (out / "background.wav").is_file()
    data = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert data["success"] is True
    assert data["modelTier"] == tier


@pytest.mark.parametrize("bad_tier", ["Free", "Pro", "Premium", "basic", "BASIC", " Basic "])
def test_rejects_invalid_model_tiers(bad_tier, tmp_path):
    # Invalid logical tiers are rejected by argparse (exit code 2) before any run.
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "--input",
                str(tmp_path / "in.wav"),
                "--output-dir",
                str(tmp_path / "out"),
                "--model-tier",
                bad_tier,
            ]
        )
    assert exc.value.code == 2


@pytest.mark.parametrize(
    "bad_tier",
    [
        "/models/vocals.pt",
        "C:\\models\\demucs.pth",
        "backend/ai/checkpoints/model.safetensors",
        "s3://bucket/key",
        "http://example.com/model.pt",
        "model.onnx",
    ],
)
def test_rejects_pathlike_url_storage_model_tier(bad_tier, tmp_path):
    # A path / URL / storage / checkpoint value for --model-tier is not an
    # accepted choice, so argparse rejects it (exit code 2).
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "--input",
                str(tmp_path / "in.wav"),
                "--output-dir",
                str(tmp_path / "out"),
                "--model-tier",
                bad_tier,
            ]
        )
    assert exc.value.code == 2


@pytest.mark.parametrize(
    "extra",
    [
        ["--checkpoint", "/models/x.pt"],
        ["--checkpoint-path", "x.pt"],
        ["--checkpoint-id", "abc123"],
        ["--checkpoint-filename", "model.safetensors"],
        ["--model", "demucs"],
        ["--url", "http://example.com/model.pt"],
        ["--s3-path", "s3://bucket/key"],
        ["--storage-key", "some/key"],
    ],
)
def test_rejects_checkpoint_and_storage_like_flags(extra, tmp_path):
    # The CLI defines no checkpoint/URL/storage flags, so any such attempt is an
    # unrecognized argument -> argparse exit code 2, before any run.
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "--input",
                str(tmp_path / "in.wav"),
                "--output-dir",
                str(tmp_path / "out"),
                "--model-tier",
                "Basic",
                *extra,
            ]
        )
    assert exc.value.code == 2


# --- safe failure paths --------------------------------------------------------


def test_missing_input_fails_safely(tmp_path):
    # A nonexistent input fails safely: metrics JSON written, success=false, safe
    # reason, non-zero exit (mirrors the required smoke test).
    out = tmp_path / "out"
    code = cli.main(
        [
            "--input",
            str(tmp_path / "nonexistent.wav"),
            "--output-dir",
            str(out),
            "--model-tier",
            "Basic",
        ]
    )
    assert code == cli.EXIT_FAILURE
    data = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert data["success"] is False
    assert data["failure_reason"] == "input_not_found"


def test_real_path_decode_not_implemented(tmp_path):
    # With an existing input and no injected fakes, the first AI boundary
    # (decode) is a placeholder -> safe "<step>_not_implemented" failure metrics.
    out = tmp_path / "out"
    metrics = cli.run_benchmark(str(_existing_input(tmp_path)), str(out), "Basic")
    assert metrics.success is False
    assert metrics.failure_reason == "decode_not_implemented"
    assert (out / "metrics.json").is_file()
    # No fabricated audio outputs on the real failure path.
    assert not (out / "vocals.wav").exists()
    assert not (out / "background.wav").exists()


def test_inference_not_implemented_writes_failure_metrics(tmp_path, monkeypatch):
    # Decode injected to succeed, real inference still a placeholder: the failure
    # is genuinely at the inference step and metrics JSON is written.
    monkeypatch.setattr(audio_io, "load_audio", lambda source: audio_io.AudioBuffer())
    out = tmp_path / "out"
    metrics = cli.run_benchmark(str(_existing_input(tmp_path)), str(out), "Professional")
    assert metrics.success is False
    assert metrics.failure_reason == "inference_not_implemented"
    data = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert data["success"] is False
    assert data["failure_reason"] == "inference_not_implemented"


def test_invalid_tier_at_function_level_is_safe(tmp_path):
    # Calling run_benchmark directly with a non-logical tier yields a safe coded
    # failure (defence in depth beneath argparse) — no raise, no leak.
    out = tmp_path / "out"
    metrics = cli.run_benchmark(str(_existing_input(tmp_path)), str(out), "Enterprise")
    assert metrics.success is False
    assert metrics.failure_reason == "invalid_model_tier"
    assert metrics.model_tier is None


def test_failure_metrics_are_safe_and_have_no_leaks(tmp_path):
    # Failure metrics carry only a safe coded reason and leak no checkpoint ref,
    # path, storage key, URL, secret or traceback in any value.
    out = tmp_path / "out"
    cli.run_benchmark(str(_existing_input(tmp_path)), str(out), "Basic")
    data = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert data["failure_reason"] in _SAFE_FAILURE_REASONS
    for value in _string_values(data):
        lowered = value.lower()
        for marker in _LEAK_MARKERS:
            assert marker not in lowered, f"metrics leak {marker!r}: {value!r}"


def test_failure_output_streams_hide_internal_reference(tmp_path, capsys):
    # stdout/stderr on failure must not expose the internal checkpoint reference
    # or a traceback.
    cli.main(
        [
            "--input",
            str(tmp_path / "nonexistent.wav"),
            "--output-dir",
            str(tmp_path / "out"),
            "--model-tier",
            "Basic",
        ]
    )
    captured = capsys.readouterr()
    combined = (captured.out + captured.err).lower()
    for marker in _LEAK_MARKERS:
        assert marker not in combined, f"CLI output leaks {marker!r}"


# --- simulated success contract ------------------------------------------------


def test_simulated_success_produces_outputs_and_full_metrics(tmp_path, monkeypatch):
    # The injected success path produces both stem outputs and a complete metrics
    # JSON shape (all required keys, populated timings/sizes) without real AI.
    _inject_fake_success(monkeypatch)
    out = tmp_path / "out"
    metrics = cli.run_benchmark(str(_existing_input(tmp_path)), str(out), "Basic")

    assert metrics.success is True
    assert metrics.failure_reason is None
    assert (out / "vocals.wav").read_bytes() == _FAKE_OUTPUT_BYTES
    assert (out / "background.wav").read_bytes() == _FAKE_OUTPUT_BYTES

    data = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    for key in (
        "success",
        "failure_reason",
        "modelTier",
        "total_runtime",
        "decode_time",
        "inference_time",
        "encode_time",
        "output_sizes",
        "checkpoint_cold_start",
        "checkpoint_warm_start",
    ):
        assert key in data
    assert data["output_sizes"]["vocals"] == len(_FAKE_OUTPUT_BYTES)
    assert data["output_sizes"]["background"] == len(_FAKE_OUTPUT_BYTES)
    for key in ("total_runtime", "decode_time", "inference_time", "encode_time"):
        assert isinstance(data[key], (int, float))
        assert data[key] >= 0


def test_simulated_success_output_has_no_leaks(tmp_path, monkeypatch, capsys):
    # Even on success, neither the metrics JSON nor stdout expose the internal
    # checkpoint reference.
    _inject_fake_success(monkeypatch)
    out = tmp_path / "out"
    cli.main(
        [
            "--input",
            str(_existing_input(tmp_path)),
            "--output-dir",
            str(out),
            "--model-tier",
            "Basic",
        ]
    )
    combined = capsys.readouterr().out.lower()
    blob = (out / "metrics.json").read_text(encoding="utf-8").lower()
    for marker in ("basic-placeholder", "professional-placeholder", "placeholder"):
        assert marker not in combined
        assert marker not in blob


# --- exit codes ----------------------------------------------------------------


def test_exit_zero_on_success(tmp_path, monkeypatch):
    _inject_fake_success(monkeypatch)
    code = cli.main(
        [
            "--input",
            str(_existing_input(tmp_path)),
            "--output-dir",
            str(tmp_path / "out"),
            "--model-tier",
            "Basic",
        ]
    )
    assert code == 0


def test_nonzero_exit_on_safe_failure(tmp_path):
    code = cli.main(
        [
            "--input",
            str(tmp_path / "nope.wav"),
            "--output-dir",
            str(tmp_path / "out"),
            "--model-tier",
            "Basic",
        ]
    )
    assert code != 0


# --- git-ignore convention -----------------------------------------------------


def test_benchmark_outputs_are_git_ignored():
    # Generated benchmark outputs must be ignored by Git. The repo .gitignore is
    # outside the backend container build context, so locate it by walking up;
    # skip only when it is genuinely absent (e.g. inside the backend image).
    here = Path(__file__).resolve()
    gitignore = None
    for parent in here.parents:
        candidate = parent / ".gitignore"
        if candidate.is_file():
            gitignore = candidate
            break
    if gitignore is None:
        pytest.skip("repo .gitignore not present in this build context")
    assert "benchmark-output/" in gitignore.read_text(encoding="utf-8")


# --- optional local Basic prototype path (P1-004B) -----------------------------
# These exercise the opt-in --use-local-model flag WITHOUT a real checkpoint,
# torch or LOCAL_MODEL_ROOT: the local path fails safely before any model load.


def test_local_flag_without_root_fails_safely_and_hides_path(tmp_path, monkeypatch, capsys):
    # --use-local-model Basic with no LOCAL_MODEL_ROOT -> safe coded failure, no
    # path leak, non-zero exit; the config check happens before any torch import.
    monkeypatch.delenv("LOCAL_MODEL_ROOT", raising=False)
    out = tmp_path / "out"
    code = cli.main(
        [
            "--input",
            str(_existing_input(tmp_path)),
            "--output-dir",
            str(out),
            "--model-tier",
            "Basic",
            "--use-local-model",
        ]
    )
    assert code == cli.EXIT_FAILURE
    data = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert data["success"] is False
    assert data["failure_reason"] == cli.FAILURE_LOCAL_MODEL_NOT_CONFIGURED
    # No local path / checkpoint leak in metrics or stdout/stderr.
    combined = (capsys.readouterr().out + capsys.readouterr().err).lower()
    for value in _string_values(data):
        lowered = value.lower()
        for marker in _LEAK_MARKERS:
            assert marker not in lowered
    for marker in ("best_model", "local_model_root", "\\", "/models"):
        assert marker not in combined


def test_local_flag_professional_is_not_implemented(tmp_path, monkeypatch):
    # Professional + --use-local-model must NOT be presented as implemented: it
    # returns a safe "professional_not_implemented" reason and never success.
    monkeypatch.delenv("LOCAL_MODEL_ROOT", raising=False)
    out = tmp_path / "out"
    metrics = cli.run_benchmark(
        str(_existing_input(tmp_path)),
        str(out),
        "Professional",
        use_local_model=True,
    )
    assert metrics.success is False
    assert metrics.failure_reason == cli.FAILURE_PROFESSIONAL_NOT_IMPLEMENTED


@pytest.mark.parametrize(
    "extra",
    [
        ["--use-best-model", "/models/x.pt"],   # boolean flag takes no value
        ["--no-use-best-model", "model.pt"],
        ["--use-local-model", "s3://bucket/key"],
    ],
)
def test_new_local_flags_reject_pathlike_values(extra, tmp_path):
    # The new flags are switches/booleans: any attached path/URL/storage value is
    # an unexpected argument -> argparse exit code 2, before any run.
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "--input",
                str(tmp_path / "in.wav"),
                "--output-dir",
                str(tmp_path / "out"),
                "--model-tier",
                "Basic",
                *extra,
            ]
        )
    assert exc.value.code == 2


def test_default_behavior_unchanged_without_local_flag(tmp_path):
    # Regression: with no --use-local-model, the Basic real path is still the
    # existing placeholder boundary -> decode_not_implemented (behavior intact).
    out = tmp_path / "out"
    metrics = cli.run_benchmark(str(_existing_input(tmp_path)), str(out), "Basic")
    assert metrics.success is False
    assert metrics.failure_reason == "decode_not_implemented"
