"""P1-004B local inference adapter tests.

Prove the adapter boundary WITHOUT a real checkpoint, real audio or torch:

- it imports with no heavy library (torch is lazy);
- a missing ``LOCAL_MODEL_ROOT`` fails safely (no path in the message) *before*
  any model load;
- driven entirely by mocks/synthetic state, it returns exactly the two in-scope
  stems (Vocals + Background), writes their two output files, and never loads a
  real checkpoint;
- its signature accepts a boolean selector, never a checkpoint path/filename/URL.

The heavy internals (load_local_model / separate_waveform / audio decode+encode)
are monkeypatched, so nothing real runs and no external service is touched.
"""

import inspect
import subprocess
import sys

import pytest

from ai import audio_io, local_inference
from ai.model import Stem

_ENV = "LOCAL_MODEL_ROOT"


def test_module_imports_without_torch():
    code = (
        "import sys, ai.local_inference\n"
        "sys.exit(1 if 'torch' in sys.modules else 0)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, "importing ai.local_inference must not import torch"


def test_missing_root_fails_safely_before_any_model_load(monkeypatch, tmp_path):
    # No LOCAL_MODEL_ROOT: config error is raised (safe, no path), and it happens
    # before torch/audio — so this runs with no heavy dependency installed.
    monkeypatch.delenv(_ENV, raising=False)
    with pytest.raises(local_inference.LocalModelConfigError) as exc:
        local_inference.run_local_separation(
            str(tmp_path / "in.wav"), str(tmp_path / "out"), use_best_model=True
        )
    assert str(tmp_path) not in str(exc.value)


def test_adapter_returns_exactly_two_stems_with_mocks(monkeypatch, tmp_path):
    # Fully mocked: no real checkpoint, no torch, no real audio.
    calls = {"loaded": False, "model": object()}

    def _fake_load(use_best_model):
        calls["loaded"] = True
        calls["use_best_model"] = use_best_model
        return calls["model"]

    def _fake_separate(model, waveform):
        # The adapter must feed our (mock) loaded model into separation.
        assert model is calls["model"]
        return ("VOCALS_WAVE", "BACKGROUND_WAVE")

    monkeypatch.setattr(local_inference, "load_local_model", _fake_load)
    monkeypatch.setattr(local_inference, "separate_waveform", _fake_separate)
    monkeypatch.setattr(audio_io, "load_mono", lambda source: "SYNTHETIC_WAVE")

    saved = {}

    def _fake_save(destination, waveform, sample_rate=audio_io.SAMPLE_RATE):
        saved[destination] = waveform
        with open(destination, "wb") as handle:
            handle.write(b"FAKE-WAV")

    monkeypatch.setattr(audio_io, "save_wav", _fake_save)

    out = tmp_path / "out"
    result = local_inference.run_local_separation(
        str(tmp_path / "in.wav"), str(out), use_best_model=True
    )

    # Exactly the two in-scope stems, and both files were written.
    assert set(result) == {Stem.VOCALS, Stem.BACKGROUND}
    assert (out / "vocals.wav").is_file()
    assert (out / "background.wav").is_file()
    # The mock model was used and separation received the right waves.
    assert calls["loaded"] is True and calls["use_best_model"] is True
    assert saved[result[Stem.VOCALS]] == "VOCALS_WAVE"
    assert saved[result[Stem.BACKGROUND]] == "BACKGROUND_WAVE"


def test_only_two_output_filenames_exist():
    assert set(local_inference._OUTPUT_FILENAMES) == {Stem.VOCALS, Stem.BACKGROUND}


def test_run_local_separation_signature_has_no_checkpoint_path_param():
    params = inspect.signature(local_inference.run_local_separation).parameters
    assert set(params) == {"input_path", "output_dir", "use_best_model"}
    for name in params:
        for banned in ("checkpoint", "url", "storage", "key"):
            assert banned not in name


def test_audio_io_local_helpers_are_importable():
    # The local audio helpers exist and are callable without any external service.
    for name in ("load_mono", "stft", "istft", "save_wav"):
        assert callable(getattr(audio_io, name))
