"""Local Basic prototype inference adapter (P1-004B).

The minimal boundary the benchmark can call *later* (P1-004C) to run the approved
local Basic model on a local audio file and return exactly the two in-scope stems
(**Vocals + Background**). It ties together the pieces without doing any real work
in P1-004B:

- :func:`load_local_model` — resolve the internal checkpoint path (server-side,
  never exposed), build the architecture and load weights **safely**;
- :func:`separate_waveform` — run the model and split into vocals/background;
- :func:`run_local_separation` — the adapter entry point used by the CLI.

Heavy deps (torch / numpy / librosa / soundfile) are imported **lazily** inside
the functions, so importing this module needs none of them. No checkpoint is
loaded and no audio is processed at import time. Local prototype only (DEC-0004):
not production-approved, not a Professional tier, connects to nothing (no API, DB,
queue, Redis, S3/MinIO, frontend or worker).

Path safety: the checkpoint path is resolved and used **only inside this backend
runtime**; it is never returned to callers, printed, put in metrics, or included
in exception messages. Callers pass a boolean ``use_best_model`` selector — never
a checkpoint path, filename, URL or storage key.
"""

from __future__ import annotations

import os

from . import audio_io, local_checkpoint, local_model
from .local_checkpoint import (  # noqa: F401  (re-exported for callers/tests)
    LocalCheckpointNotFoundError,
    LocalModelConfigError,
    LocalModelError,
)
from .model import Stem

# Fixed local output filenames for the two in-scope stems (never extra stems).
_OUTPUT_FILENAMES = {
    Stem.VOCALS: "vocals.wav",
    Stem.BACKGROUND: "background.wav",
}

_TORCH_MISSING_MESSAGE = (
    "PyTorch is required to run the local prototype adapter but is not installed "
    "in this environment."
)


class LocalDependencyError(LocalModelError):
    """A required local-prototype dependency (e.g. torch) is unavailable. No path."""


def _safe_torch_load(torch, checkpoint_path):
    """Load a checkpoint preferring the safe ``weights_only=True`` path.

    DEC-0004 §9: loading a ``.pt`` file carries pickle / deserialization risk, so
    we prefer ``weights_only=True`` (torch >= 2.x). The approved local checkpoint
    is a plain state_dict, so that path is expected to succeed. The fallback (for
    older torch without the kwarg) is a documented local-prototype risk and is
    only ever used against the vetted local out-of-band checkpoint — never an
    untrusted path. The ``checkpoint_path`` is never surfaced by this module.
    """
    try:
        return torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    except TypeError:
        # Older torch: no weights_only kwarg. Local approved checkpoint only.
        return torch.load(checkpoint_path, map_location="cpu")


def load_local_model(use_best_model: bool):
    """Resolve, build and load the local Basic prototype model. Server-side only.

    Resolves the internal checkpoint path from the boolean selector (config is
    checked first, so a missing ``LOCAL_MODEL_ROOT`` fails safely *before* any
    torch import), builds the architecture and loads weights via
    :func:`_safe_torch_load`. Returns an eval-mode ``torch.nn.Module``. The
    resolved path is never returned or logged. Not exercised in P1-004B tests
    (they mock this); real loading happens in P1-004C.
    """
    checkpoint_path = local_checkpoint.resolve_checkpoint_path(use_best_model)
    try:
        import torch
    except ImportError as exc:
        raise LocalDependencyError(_TORCH_MISSING_MESSAGE) from exc

    model = local_model.build_model()
    state = _safe_torch_load(torch, checkpoint_path)
    # Accept either a training checkpoint dict or a raw state_dict (reference layout).
    if isinstance(state, dict) and "model_state_dict" in state:
        state_dict = state["model_state_dict"]
    else:
        state_dict = state
    model.load_state_dict(state_dict)
    return model.eval()


def separate_waveform(model, waveform):
    """Run the model on a mono ``waveform`` and return (vocals, background).

    Vocals = mask * spectrogram; Background = (1 - mask) * spectrogram, then ISTFT
    back to waveforms of the original length. Lazy-imports numpy + torch (audio
    STFT/ISTFT via :mod:`ai.audio_io`). Not exercised in P1-004B tests (mocked).
    """
    import numpy as np
    import torch

    spectrogram = audio_io.stft(waveform)
    magnitude = np.abs(spectrogram)
    magnitude_tensor = torch.from_numpy(magnitude)[None, None, :, :]
    with torch.no_grad():
        mask = model(magnitude_tensor)
    mask = mask[0, 0].cpu().numpy()

    vocals_spec = mask * spectrogram
    background_spec = (1.0 - mask) * spectrogram
    length = len(waveform)
    vocals_wave = audio_io.istft(vocals_spec, length=length)
    background_wave = audio_io.istft(background_spec, length=length)
    return vocals_wave, background_wave


def run_local_separation(
    input_path: str, output_dir: str, *, use_best_model: bool
) -> dict[Stem, str]:
    """Adapter entry point: separate ``input_path`` into Vocals + Background WAVs.

    Loads the local model (server-side checkpoint resolution), decodes the local
    audio, separates it and writes exactly two output files, returning a mapping
    of :class:`ai.model.Stem` to its **local** output path (server-side; the CLI
    never surfaces these to users/metrics as checkpoint info). Raises safe
    :class:`LocalModelError` subclasses (config / checkpoint / dependency) whose
    messages contain no local path. In P1-004B this is only driven by mocks; the
    real end-to-end run is P1-004C.
    """
    model = load_local_model(use_best_model)
    waveform = audio_io.load_mono(input_path)
    vocals_wave, background_wave = separate_waveform(model, waveform)

    os.makedirs(output_dir, exist_ok=True)
    outputs: dict[Stem, str] = {}
    for stem, wave in (
        (Stem.VOCALS, vocals_wave),
        (Stem.BACKGROUND, background_wave),
    ):
        destination = os.path.join(output_dir, _OUTPUT_FILENAMES[stem])
        audio_io.save_wav(destination, wave)
        outputs[stem] = destination
    return outputs
