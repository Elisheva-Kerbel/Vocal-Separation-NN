"""P1-004B local checkpoint resolution tests.

Prove the local prototype checkpoint boundary WITHOUT any heavy dependency, real
checkpoint or real path:

- ``LOCAL_MODEL_ROOT`` is required; missing/empty fails safely;
- no safe failure message exposes the actual local path;
- the ``use_best_model`` boolean selector picks ``best_model.pt`` (true) or the
  basic slot (false), and the basic slot's temporary reuse is documented + tested;
- the selector accepts only a bool — a raw path / filename / URL / storage-key
  string is rejected, so checkpoint naming stays server-side.

Stdlib only: importing the module under test pulls in no torch/librosa/soundfile/
numpy (asserted below), and nothing is loaded or downloaded.
"""

import inspect
import subprocess
import sys

import pytest

import ai.local_checkpoint as lc

_ENV = lc.ENV_MODEL_ROOT

# Markers that would betray a leaked local path / filename in a "safe" message.
_PATH_MARKERS = ("/", "\\", "best_model", ".pt", "checkpoints", "C:", "~", "root=")


# --- LOCAL_MODEL_ROOT is required, and fails safely --------------------------


def test_missing_root_raises_config_error(monkeypatch):
    monkeypatch.delenv(_ENV, raising=False)
    with pytest.raises(lc.LocalModelConfigError):
        lc.resolve_checkpoint_path(True)


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_blank_root_raises_config_error(monkeypatch, blank):
    monkeypatch.setenv(_ENV, blank)
    with pytest.raises(lc.LocalModelConfigError):
        lc.resolve_checkpoint_path(True)


def test_missing_root_message_has_no_path(monkeypatch):
    monkeypatch.delenv(_ENV, raising=False)
    with pytest.raises(lc.LocalModelConfigError) as exc:
        lc.resolve_checkpoint_path(True)
    msg = str(exc.value)
    # Names the env var to set, but leaks no concrete path / filename.
    assert _ENV in msg
    for marker in ("best_model", ".pt", "checkpoints", "C:", "\\", "//"):
        assert marker not in msg


def test_missing_checkpoint_message_hides_actual_path(monkeypatch, tmp_path):
    # A configured-but-empty root: the file is absent, so a safe error is raised
    # that contains NEITHER the configured root NOR the checkpoint filename.
    monkeypatch.setenv(_ENV, str(tmp_path))
    with pytest.raises(lc.LocalCheckpointNotFoundError) as exc:
        lc.resolve_checkpoint_path(True)
    msg = str(exc.value)
    assert str(tmp_path) not in msg
    for marker in _PATH_MARKERS:
        assert marker not in msg


# --- use_best_model selector -------------------------------------------------


def test_use_best_true_selects_best_model():
    assert lc.checkpoint_filename(True) == "best_model.pt"
    assert lc.checkpoint_filename(True) == lc.BEST_MODEL_FILENAME


def test_use_best_false_selects_basic_slot():
    assert lc.checkpoint_filename(False) == lc.BASIC_SLOT_FILENAME


def test_basic_slot_is_documented_temporary_reuse_of_best_model():
    # DEC-0004 §5: the basic slot currently (temporarily) reuses best_model.pt.
    assert lc.BASIC_SLOT_IS_TEMPORARY_ALIAS is True
    assert lc.BASIC_SLOT_FILENAME == lc.BEST_MODEL_FILENAME
    assert lc.checkpoint_filename(False) == lc.checkpoint_filename(True) == "best_model.pt"


@pytest.mark.parametrize(
    "raw",
    [
        "best_model.pt",
        "/models/vocals.pt",
        "C:\\models\\demucs.pth",
        "backend/ai/checkpoints/model.safetensors",
        "s3://bucket/key",
        "http://example.com/model.pt",
        "model.onnx",
        "true",
        "1",
        1,
        0,
        None,
        1.0,
    ],
)
def test_selector_rejects_non_bool_including_pathlike(raw):
    # Only a real bool is accepted: a path / filename / URL / storage-key string
    # (or a truthy int) can never be smuggled in as a checkpoint name.
    with pytest.raises(TypeError):
        lc.checkpoint_filename(raw)


def test_resolve_signature_takes_no_path_parameter():
    params = inspect.signature(lc.resolve_checkpoint_path).parameters
    assert set(params) == {"use_best_model", "require_exists"}
    for name in params:
        for banned in ("path", "checkpoint", "file", "url", "filename"):
            assert banned not in name


def test_resolve_returns_internal_path_under_root(monkeypatch, tmp_path):
    # With the checkpoint present, resolution returns a Path *inside* the root's
    # checkpoints dir. (tmp_path is synthetic — not the real local model path.)
    ckpt_dir = tmp_path / "checkpoints"
    ckpt_dir.mkdir()
    (ckpt_dir / "best_model.pt").write_bytes(b"not-a-real-checkpoint")
    monkeypatch.setenv(_ENV, str(tmp_path))
    resolved = lc.resolve_checkpoint_path(True)
    assert resolved == ckpt_dir / "best_model.pt"
    assert resolved.is_file()


def test_require_exists_false_skips_file_check(monkeypatch, tmp_path):
    monkeypatch.setenv(_ENV, str(tmp_path))
    resolved = lc.resolve_checkpoint_path(False, require_exists=False)
    assert resolved.name == "best_model.pt"


# --- optional env selector ---------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [("true", True), ("1", True), ("yes", True), ("on", True), ("TRUE", True),
     ("false", False), ("0", False), ("no", False), ("", False), ("nonsense", False)],
)
def test_use_best_model_from_env(monkeypatch, value, expected):
    monkeypatch.setenv(lc.ENV_USE_BEST, value)
    assert lc.use_best_model_from_env(True) is expected


def test_use_best_model_from_env_default_when_unset(monkeypatch):
    monkeypatch.delenv(lc.ENV_USE_BEST, raising=False)
    assert lc.use_best_model_from_env(True) is True
    assert lc.use_best_model_from_env(False) is False


# --- import-light guarantee --------------------------------------------------


def test_local_checkpoint_imports_no_heavy_libs():
    code = (
        "import sys, ai.local_checkpoint\n"
        "forbidden = ['torch', 'librosa', 'soundfile', 'numpy', 'scipy']\n"
        "hit = [m for m in forbidden if m in sys.modules]\n"
        "print(','.join(hit))\n"
        "sys.exit(1 if hit else 0)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, f"heavy libs imported: {result.stdout!r}"
