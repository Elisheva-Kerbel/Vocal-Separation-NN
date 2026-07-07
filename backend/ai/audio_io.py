"""Audio I/O boundaries — Phase 1 (TASK-P1-001) placeholders only.

Names the decode/encode boundary the benchmark will use later. There is NO real
decoding/encoding here and NO audio dependency (no soundfile / librosa / numpy /
scipy / ...); every function is a placeholder that raises ``NotImplementedError``
until the benchmark task (P1-003) implements it.

Paths handled here are *server-side, local benchmark files* (a local audio
fixture and its output stems) — never client input and never checkpoint paths.
"""

from __future__ import annotations


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
