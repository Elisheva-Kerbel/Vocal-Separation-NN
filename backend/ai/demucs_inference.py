"""Demucs-based separation for the Professional tier.

Uses Meta's htdemucs_ft model -- the state-of-the-art open-source music source
separation model. It produces 4 stems (vocals, drums, bass, other) but we only
keep vocals and background (drums + bass + other mixed back together) to match
the project's two-stem contract.

Heavy deps (demucs, torch, torchaudio) are imported lazily so importing this
module is cheap.
"""

from __future__ import annotations

import os

from .model import Stem

_OUTPUT_FILENAMES = {
    Stem.VOCALS: "vocals.wav",
    Stem.BACKGROUND: "background.wav",
}

DEMUCS_MODEL = "htdemucs_ft"

_CACHE: dict = {}


def _device():
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_vocals_model():
    """Load and cache only the vocals specialist from the htdemucs_ft bag."""
    if "model" not in _CACHE:
        from demucs.pretrained import get_model

        bag = get_model(DEMUCS_MODEL)
        bag.eval()

        vocals_idx = bag.sources.index("vocals")
        specialist_idx = next(
            i for i, w in enumerate(bag.weights) if w[vocals_idx] == 1.0
        )
        sub = bag.models[specialist_idx].eval()
        _CACHE["model"] = sub
        _CACHE["vocals_idx"] = sub.sources.index("vocals")
        _CACHE["sr"] = sub.samplerate
    return _CACHE["model"], _CACHE["vocals_idx"], _CACHE["sr"]


def run_demucs_separation(input_path: str, output_dir: str) -> dict[Stem, str]:
    """Separate input_path into Vocals + Background using Demucs htdemucs_ft.

    Runs only the vocals specialist (about 4x faster than the full bag).
    Background is computed as mix minus vocals.
    """
    import librosa
    import soundfile as sf
    import torch
    from demucs.apply import apply_model

    model, vocals_idx, sr_model = _load_vocals_model()
    device = _device()
    model.to(device)

    wav_np, sr = librosa.load(input_path, sr=None, mono=False)
    if wav_np.ndim == 1:
        wav_np = wav_np[None, :]
    wav = torch.from_numpy(wav_np).float()

    if sr != sr_model:
        wav = torch.from_numpy(
            librosa.resample(wav.numpy(), orig_sr=sr, target_sr=sr_model)
        ).float()
        sr = sr_model

    if wav.shape[0] == 1:
        wav = wav.expand(2, -1)

    ref = wav.mean(0)
    wav_norm = (wav - ref.mean()) / (ref.std() + 1e-8)

    with torch.inference_mode():
        sources = apply_model(
            model, wav_norm[None], device=device,
            shifts=0, overlap=0.1, progress=False,
        )

    sources = sources[0] * ref.std() + ref.mean()
    vocals = sources[vocals_idx].cpu().numpy().T

    background = wav.numpy().T - vocals

    os.makedirs(output_dir, exist_ok=True)
    outputs: dict[Stem, str] = {}

    vocals_path = os.path.join(output_dir, _OUTPUT_FILENAMES[Stem.VOCALS])
    sf.write(vocals_path, vocals, sr)
    outputs[Stem.VOCALS] = vocals_path

    bg_path = os.path.join(output_dir, _OUTPUT_FILENAMES[Stem.BACKGROUND])
    sf.write(bg_path, background, sr)
    outputs[Stem.BACKGROUND] = bg_path

    return outputs
