"""Audio I/O boundaries — Phase 1.

Two layers live here:

- the original P1-001 *boundary placeholders* (:class:`AudioBuffer`,
  :func:`load_audio`, :func:`save_audio`) which stay non-executing; and
- minimal **local prototype** helpers added in P1-004B
  (:func:`load_mono`, :func:`stft`, :func:`istft`, :func:`save_wav`) used by the
  local Basic inference adapter.

Every heavy audio dependency (librosa / soundfile / numpy) is imported **lazily
inside the function body**, never at module top, so importing this module pulls
in none of them and the AI boundary stays import-light
(see ``tests/ai/test_imports.py``). No network, DB, queue, Redis or S3/MinIO
access happens here.

Paths handled here are *server-side, local benchmark files* (a local audio
fixture and its output stems) — never client input and never checkpoint paths.
"""

from __future__ import annotations

# Audio front-end constants for the local prototype, matching the local reference
# model so a later-loaded checkpoint sees consistent feature shapes.
from .local_model import HOP_LENGTH, N_FFT, SAMPLE_RATE  # noqa: F401  (re-exported)


class AudioBuffer:
    """Placeholder for decoded audio passed between decode -> inference -> encode.

    Phase 1 boundary marker only: it holds no samples and pulls in no numeric or
    audio library. Its concrete representation is defined by the benchmark task
    (P1-003).
    """


def load_audio(source: str) -> AudioBuffer:
    """Decode a local benchmark audio file into an :class:`AudioBuffer`.

    Placeholder only — no decoding happens yet and no audio library is used.
    ``source`` is a server-side local file path (the benchmark fixture), not
    client input. Implemented in Phase 1 task P1-003.
    """
    raise NotImplementedError("Audio decoding is implemented in Phase 1 task P1-003.")


def save_audio(buffer: AudioBuffer, destination: str) -> None:
    """Encode an :class:`AudioBuffer` to a local benchmark output file.

    Placeholder only — no encoding happens yet and no audio library is used.
    ``destination`` is a server-side local output path, not client input.
    Implemented in Phase 1 task P1-003.
    """
    raise NotImplementedError("Audio encoding is implemented in Phase 1 task P1-003.")


# --- Local prototype audio helpers (P1-004B) ----------------------------------
# Minimal load / STFT / ISTFT / save used by the local Basic inference adapter.
# Heavy deps (librosa / soundfile / numpy) are imported lazily inside each
# function so importing this module needs none of them. All paths are
# server-side local files (fixtures / output stems), never client input.


def load_mono(source: str, sample_rate: int = SAMPLE_RATE):
    """Load a local audio file as a mono waveform at ``sample_rate``.

    Returns a 1-D numpy float array. ``source`` is a server-side local path (a
    benchmark fixture), never client input. Lazy-imports librosa.
    """
    import librosa

    waveform, _ = librosa.load(source, sr=sample_rate, mono=True)
    return waveform


def stft(waveform):
    """Complex STFT of a mono waveform (librosa, lazy import)."""
    import librosa

    return librosa.stft(waveform, n_fft=N_FFT, hop_length=HOP_LENGTH)


def istft(spectrogram, length: int | None = None):
    """Inverse STFT back to a waveform, optionally to a fixed ``length``."""
    import librosa

    return librosa.istft(spectrogram, hop_length=HOP_LENGTH, length=length)


def save_wav(destination: str, waveform, sample_rate: int = SAMPLE_RATE) -> None:
    """Write a mono waveform to a local WAV file, clipped to [-1, 1].

    ``destination`` is a server-side local output path (e.g. ``vocals.wav`` /
    ``background.wav``), never client input and never a checkpoint path.
    Lazy-imports soundfile + numpy.
    """
    import numpy as np
    import soundfile as sf

    sf.write(destination, np.clip(waveform, -1.0, 1.0), sample_rate)
