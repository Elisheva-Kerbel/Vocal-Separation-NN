"""Local demo backend slice (FAST-DEMO-003) — LOCAL DEMO ONLY.

Authorized by ``docs/decisions/DEC-0009-local-demo-vertical-slice.md``: the demo is
the only place where AI inference may run inside an HTTP request (DEC-0009 §3 D1)
and the only routes outside ``/health`` (§5). It is **not** production, **not**
commercial, **not** a Professional tier, and it introduces **no** auth, DB write,
queue, worker, Redis, MinIO/S3 or storage client.

Two routes, nothing else:

- ``POST /demo/separate`` — raw request body in, Vocals + Background out.
- ``GET  /demo/jobs/{job_id}/stems/{stem}`` — backend-mediated file response.

Safety properties (DEC-0009 §4, §5):

- The upload body is read from ``request.stream()`` and capped **while** buffering,
  so an oversized upload is rejected without reading it all.
- **No client string ever becomes a path segment.** The input is stored under a
  server-generated UUID with a fixed filename; the client's filename is not used at
  all. ``job_id`` is validated as a UUID and ``stem`` against the existing two-value
  ``Stem`` enum, so a traversal-style value is rejected before any filesystem access.
- Output paths come from the adapter's own return value — this module never builds
  or guesses a checkpoint path, and never returns a filesystem path, storage key or
  checkpoint reference. Every failure maps to a fixed, safe coded reason.
- Heavy AI deps stay lazy: importing this module imports no torch/librosa/soundfile
  (the ``ai`` boundary keeps them inside function bodies).
"""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse

from ai import local_checkpoint, local_inference
from ai.model import Stem

router = APIRouter(prefix="/demo", tags=["demo"])

# Container-side defaults (DEC-0009 §7, §8). Both are read at call time, not import
# time, so the operator can override them without touching code.
DEFAULT_DATA_DIR = "/app/local-data/demo"
DEFAULT_MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB

# Accepted upload content types (DEC-0009 §8). WAV and MP3 both work in the current
# image; ``application/octet-stream`` covers browsers that send no specific type.
ACCEPTED_CONTENT_TYPES = frozenset(
    {
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/x-wav",
        "application/octet-stream",
    }
)

# Fixed name for the stored upload. The client's filename is deliberately unused, so
# no client-controlled string can influence the path.
_INPUT_FILENAME = "input"

# In-process demo state only (DEC-0009 §4, §6-storage): job id -> {stem: local path}.
# No database, no persistence — results are ephemeral and vanish with the process.
_JOBS: dict[str, dict[str, str]] = {}

# Exception module roots that indicate a decode/format problem with the *upload*
# (a bad or unsupported file) rather than a server fault. Matched by module name so
# no audio library has to be imported here.
_DECODE_ERROR_MODULES = ("soundfile", "librosa", "audioread")


def _data_dir() -> Path:
    return Path(os.getenv("DEMO_DATA_DIR") or DEFAULT_DATA_DIR)


def _max_upload_bytes() -> int:
    raw = os.getenv("DEMO_MAX_UPLOAD_BYTES")
    return int(raw) if raw else DEFAULT_MAX_UPLOAD_BYTES


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    """Safe error response: a fixed code plus fixed text.

    Never carries a path, checkpoint reference, storage key, secret, echoed client
    input or traceback (DEC-0009 §4).
    """
    return JSONResponse(status_code=status_code, content={"error": code, "message": message})


def _separation_error(exc: Exception) -> JSONResponse:
    """Map an adapter failure to a safe coded response. No detail escapes."""
    if isinstance(exc, local_checkpoint.LocalModelConfigError):
        return _error(503, "local_model_not_configured", "Local demo model is not configured.")
    if isinstance(exc, local_checkpoint.LocalCheckpointNotFoundError):
        return _error(503, "local_checkpoint_unavailable", "Local demo model is unavailable.")
    if isinstance(exc, local_inference.LocalDependencyError):
        return _error(503, "local_dependency_missing", "Local demo model is unavailable.")
    if type(exc).__module__.split(".")[0] in _DECODE_ERROR_MODULES:
        return _error(400, "unsupported_or_corrupt_audio", "The uploaded audio could not be read.")
    return _error(500, "separation_failed", "Separation failed. Please try again.")


def _discard_previous_jobs(data_dir: Path) -> None:
    """Minimal demo cleanup (DEC-0009 §7): keep only the newest job's files."""
    for previous_id in list(_JOBS):
        shutil.rmtree(data_dir / previous_id, ignore_errors=True)
    _JOBS.clear()


@router.post("/separate")
async def separate(request: Request) -> Response:
    """Separate a raw-body upload into Vocals + Background, synchronously.

    Raw body only — no multipart, so no ``python-multipart`` dependency is needed
    (DEC-0009 §8). The Basic tier is fixed server-side: the client sends no tier, no
    checkpoint reference and no path.
    """
    content_type = (request.headers.get("content-type") or "application/octet-stream")
    if content_type.split(";")[0].strip().lower() not in ACCEPTED_CONTENT_TYPES:
        return _error(415, "unsupported_media_type", "Upload a WAV or MP3 audio file.")

    # Cap while streaming so an oversized upload is rejected without buffering it all.
    max_bytes = _max_upload_bytes()
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > max_bytes:
            return _error(413, "payload_too_large", "The uploaded file is too large.")
    if not body:
        return _error(400, "empty_body", "No audio was uploaded.")

    job_id = str(uuid.uuid4())
    data_dir = _data_dir()
    _discard_previous_jobs(data_dir)
    job_dir = data_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    input_path = job_dir / _INPUT_FILENAME
    input_path.write_bytes(bytes(body))

    try:
        # CPU-bound work off the event loop; the adapter is used exactly as-is and
        # resolves its checkpoint server-side from the boolean selector.
        outputs = await run_in_threadpool(
            local_inference.run_local_separation,
            str(input_path),
            str(job_dir),
            use_best_model=local_checkpoint.use_best_model_from_env(True),
        )
    except Exception as exc:  # noqa: BLE001 - every failure must be a safe coded response
        shutil.rmtree(job_dir, ignore_errors=True)
        return _separation_error(exc)

    _JOBS[job_id] = {stem.value: str(path) for stem, path in outputs.items()}
    return JSONResponse(
        {
            "jobId": job_id,
            "status": "ready",
            "stems": [
                {"stem": stem.value, "url": f"/demo/jobs/{job_id}/stems/{stem.value}"}
                for stem in (Stem.VOCALS, Stem.BACKGROUND)
            ],
        }
    )


@router.get("/jobs/{job_id}/stems/{stem}")
def stem_file(job_id: uuid.UUID, stem: Stem) -> Response:
    """Stream one stem back through the backend.

    ``job_id`` (UUID) and ``stem`` (Vocals or Background only) are validated by
    FastAPI before this runs, and the file path is looked up from server-side state —
    never composed from client input. No static mount, no public or permanent URL.
    """
    path = _JOBS.get(str(job_id), {}).get(stem.value)
    if path is None or not os.path.isfile(path):
        return _error(404, "job_not_found", "No demo result is available for this job.")
    return FileResponse(path, media_type="audio/wav")
