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
    """Load a checkpoint with weights_only=True for safety."""
    return torch.load(checkpoint_path, map_location="cpu", weights_only=True)


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
    if isinstance(state, dict) and "model_state_dict" in state:
        state_dict = state["model_state_dict"]
    else:
        state_dict = state
    model.load_state_dict(state_dict)
    model.eval()
    model = model.to(memory_format=torch.channels_last)
    return model


def _predict_mask(model, mag_tensor, chunk_frames=256, overlap=16, batch_size=4):
    """Run the model in time-chunks for lower peak memory and better cache use."""
    import torch

    F, Tt = mag_tensor.shape[-2:]
    step = chunk_frames - 2 * overlap
    pad = (-Tt) % step
    x = torch.nn.functional.pad(mag_tensor, (overlap, overlap + pad))
    out = torch.empty(1, 1, F, Tt + pad)
    starts = list(range(0, x.shape[-1] - chunk_frames + 1, step))
    with torch.inference_mode():
        for i in range(0, len(starts), batch_size):
            sl = starts[i:i + batch_size]
            b = torch.cat([x[..., s:s + chunk_frames] for s in sl], 0).contiguous(
                memory_format=torch.channels_last)
            m = model(b)
            for j, s in enumerate(sl):
                out[..., s:s + step] = m[j:j + 1, :, :, overlap:overlap + step]
    return out[..., :Tt]


def separate_waveform(model, waveform):
    """Run the model on a mono ``waveform`` and return (vocals, background).

    Uses chunked inference for lower peak memory (about 1 GB vs 2.6 GB) and
    about 3x faster forward pass. Background is computed as waveform minus
    vocals, skipping a redundant ISTFT.
    """
    import numpy as np
    import torch

    spectrogram = audio_io.stft(waveform)
    magnitude = np.abs(spectrogram)
    magnitude_tensor = torch.from_numpy(magnitude)[None, None, :, :]

    mask = _predict_mask(model, magnitude_tensor)[0, 0].cpu().numpy()

    vocals_spec = mask * spectrogram
    length = len(waveform)
    vocals_wave = audio_io.istft(vocals_spec, length=length)
    background_wave = waveform - vocals_wave
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
