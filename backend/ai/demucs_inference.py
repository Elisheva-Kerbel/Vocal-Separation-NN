"""Demucs-based separation for the Professional tier.

Uses Meta's htdemucs_ft model — the state-of-the-art open-source music source
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


def run_demucs_separation(input_path: str, output_dir: str) -> dict[Stem, str]:
    """Separate input_path into Vocals + Background using Demucs htdemucs_ft.

    Returns a mapping of Stem -> local output path.
    """
    import ssl
    import urllib.request

    import librosa
    import numpy as np
    import soundfile as sf
    import torch
    from demucs.apply import apply_model
    from demucs.pretrained import get_model

    # Bypass SSL verification for corporate proxy (self-signed cert in chain).
    # Patch at every level: ssl module globals, urllib (torch.hub), requests (HF Hub).
    orig_create_ctx = ssl.create_default_context
    orig_https_ctx = ssl._create_default_https_context

    def _no_verify_context(*a, **kw):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    ssl.create_default_context = _no_verify_context
    ssl._create_default_https_context = _no_verify_context
    os.environ["CURL_CA_BUNDLE"] = ""
    os.environ["REQUESTS_CA_BUNDLE"] = ""
    os.environ["HF_HUB_DISABLE_SSL_VERIFY"] = "1"
    os.environ["PYTHONHTTPSVERIFY"] = "0"

    try:
        import requests as _req
        _orig_req_get = _req.Session.request
        def _no_verify_request(self, *a, **kw):
            kw.setdefault("verify", False)
            return _orig_req_get(self, *a, **kw)
        _req.Session.request = _no_verify_request
    except ImportError:
        _orig_req_get = None

    try:
        model = get_model(DEMUCS_MODEL)
    finally:
        ssl.create_default_context = orig_create_ctx
        ssl._create_default_https_context = orig_https_ctx
        os.environ.pop("CURL_CA_BUNDLE", None)
        os.environ.pop("REQUESTS_CA_BUNDLE", None)
        os.environ.pop("HF_HUB_DISABLE_SSL_VERIFY", None)
        os.environ.pop("PYTHONHTTPSVERIFY", None)
        if _orig_req_get is not None:
            _req.Session.request = _orig_req_get
    model.eval()

    # Use librosa for audio loading (supports MP3/WAV/M4A without torchcodec)
    wav_np, sr = librosa.load(input_path, sr=None, mono=False)
    if wav_np.ndim == 1:
        wav_np = wav_np[None, :]
    wav = torch.from_numpy(wav_np).float()

    if sr != model.samplerate:
        wav = torch.from_numpy(
            librosa.resample(wav.numpy(), orig_sr=sr, target_sr=model.samplerate)
        ).float()
        sr = model.samplerate

    if wav.dim() == 1:
        wav = wav.unsqueeze(0)
    if wav.shape[0] == 1:
        wav = wav.expand(2, -1)

    ref = wav.mean(0)
    wav = (wav - ref.mean()) / (ref.std() + 1e-8)

    with torch.no_grad():
        sources = apply_model(model, wav[None], device="cpu", progress=False)

    sources = sources[0]
    sources = sources * ref.std() + ref.mean()

    source_names = model.sources
    vocals_idx = source_names.index("vocals")
    vocals = sources[vocals_idx].cpu().numpy().T

    bg_indices = [i for i, name in enumerate(source_names) if name != "vocals"]
    background = sum(sources[i] for i in bg_indices).cpu().numpy().T

    os.makedirs(output_dir, exist_ok=True)
    outputs: dict[Stem, str] = {}

    vocals_path = os.path.join(output_dir, _OUTPUT_FILENAMES[Stem.VOCALS])
    sf.write(vocals_path, vocals, sr)
    outputs[Stem.VOCALS] = vocals_path

    bg_path = os.path.join(output_dir, _OUTPUT_FILENAMES[Stem.BACKGROUND])
    sf.write(bg_path, background, sr)
    outputs[Stem.BACKGROUND] = bg_path

    return outputs
