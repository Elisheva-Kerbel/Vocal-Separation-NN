"""FAST-DEMO-003 local demo slice tests (DEC-0009 §9).

Everything here runs with **mocked inference**: no torch, no checkpoint, no
``/models`` mount and no real audio are required. The tests prove the two demo
routes behave, that every rejection path is a safe coded error, and that no
response ever leaks a path, checkpoint reference, storage key or secret.
"""

import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ai import local_checkpoint, local_inference
from ai.model import Stem
from app import demo
from app.main import app

client = TestClient(app)

WAV_HEADERS = {"content-type": "audio/wav"}
AUDIO_BYTES = b"fake-upload-bytes"

# Markers that must never appear in any demo response (DEC-0009 §4).
FORBIDDEN_MARKERS = (
    "LOCAL_MODEL_ROOT",
    "/models",
    "/app/",
    "checkpoints",
    "best_model",
    ".pt",
    "storage_key",
    "DATABASE_URL",
    "password",
    "secret",
    "token",
    "Traceback",
)


def assert_no_leak(response):
    body = response.text
    for marker in FORBIDDEN_MARKERS:
        assert marker not in body, f"{marker!r} leaked in {body!r}"


def fake_separation(input_path, output_dir, *, use_best_model):
    """Stand-in for the real adapter: writes the two stems, returns their paths."""
    assert Path(input_path).is_file()
    outputs = {}
    for stem in (Stem.VOCALS, Stem.BACKGROUND):
        destination = Path(output_dir) / f"{stem.value}.wav"
        destination.write_bytes(b"RIFF-fake-wav-bytes")
        outputs[stem] = str(destination)
    return outputs


@pytest.fixture
def demo_env(monkeypatch, tmp_path):
    """Point demo storage at a temp dir and start from empty in-process state."""
    monkeypatch.setenv("DEMO_DATA_DIR", str(tmp_path))
    demo._JOBS.clear()
    yield tmp_path
    demo._JOBS.clear()


@pytest.fixture
def mocked_separation(monkeypatch, demo_env):
    monkeypatch.setattr(local_inference, "run_local_separation", fake_separation)
    return demo_env


def separate(**kwargs):
    kwargs.setdefault("headers", WAV_HEADERS)
    kwargs.setdefault("content", AUDIO_BYTES)
    return client.post("/demo/separate", **kwargs)


# --- 1. POST happy path ------------------------------------------------------


def test_separate_happy_path(mocked_separation):
    response = separate()
    assert response.status_code == 200
    payload = response.json()

    job_id = payload["jobId"]
    assert uuid.UUID(job_id)  # opaque UUID, not a name or path
    assert payload["status"] == "ready"

    # Exactly the two in-scope stems, in order, and no third stem.
    assert [entry["stem"] for entry in payload["stems"]] == ["vocals", "background"]
    for entry in payload["stems"]:
        assert entry["url"] == f"/demo/jobs/{job_id}/stems/{entry['stem']}"
    assert_no_leak(response)


def test_separate_response_carries_no_path_or_storage_field(mocked_separation):
    payload = separate().json()
    assert set(payload) == {"jobId", "status", "stems"}
    for entry in payload["stems"]:
        assert set(entry) == {"stem", "url"}


# --- 2. GET stem happy path --------------------------------------------------


@pytest.mark.parametrize("stem", ["vocals", "background"])
def test_get_stem_returns_audio_bytes(mocked_separation, stem):
    job_id = separate().json()["jobId"]
    response = client.get(f"/demo/jobs/{job_id}/stems/{stem}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content == b"RIFF-fake-wav-bytes"
    assert_no_leak(response)


# --- 3./4. Unknown job and invalid stem --------------------------------------


def test_unknown_job_id_is_404_and_safe(demo_env):
    response = client.get(f"/demo/jobs/{uuid.uuid4()}/stems/vocals")
    assert response.status_code == 404
    assert response.json()["error"] == "job_not_found"
    assert_no_leak(response)


def test_non_uuid_job_id_is_rejected_and_safe(demo_env):
    response = client.get("/demo/jobs/not-a-uuid/stems/vocals")
    assert response.status_code in (404, 422)
    assert_no_leak(response)


@pytest.mark.parametrize("stem", ["drums", "piano", "../../etc/passwd"])
def test_invalid_stem_is_rejected_and_safe(mocked_separation, stem):
    job_id = separate().json()["jobId"]
    response = client.get(f"/demo/jobs/{job_id}/stems/{stem}")
    assert response.status_code in (404, 422)
    assert_no_leak(response)


# --- 5./6./7. Body and content-type rejections -------------------------------


def test_empty_body_is_400(demo_env):
    response = separate(content=b"")
    assert response.status_code == 400
    assert response.json()["error"] == "empty_body"
    assert_no_leak(response)


@pytest.mark.parametrize("content_type", ["text/plain", "application/json", "image/png"])
def test_unsupported_content_type_is_415(demo_env, content_type):
    response = separate(headers={"content-type": content_type})
    assert response.status_code == 415
    assert response.json()["error"] == "unsupported_media_type"
    assert_no_leak(response)


def test_oversized_body_is_413(monkeypatch, demo_env):
    monkeypatch.setenv("DEMO_MAX_UPLOAD_BYTES", "16")
    response = separate(content=b"x" * 64)
    assert response.status_code == 413
    assert response.json()["error"] == "payload_too_large"
    assert_no_leak(response)


def test_oversized_upload_is_not_stored(monkeypatch, demo_env):
    monkeypatch.setenv("DEMO_MAX_UPLOAD_BYTES", "16")
    separate(content=b"x" * 64)
    assert list(demo_env.iterdir()) == []


# --- 8. Model/checkpoint failures --------------------------------------------


@pytest.mark.parametrize(
    ("exception", "code"),
    [
        (local_checkpoint.LocalModelConfigError("no root"), "local_model_not_configured"),
        (local_checkpoint.LocalCheckpointNotFoundError("missing"), "local_checkpoint_unavailable"),
        (local_inference.LocalDependencyError("no torch"), "local_dependency_missing"),
    ],
)
def test_model_failures_are_safe_503(monkeypatch, demo_env, exception, code):
    def _raise(*args, **kwargs):
        raise exception

    monkeypatch.setattr(local_inference, "run_local_separation", _raise)
    response = separate()
    assert response.status_code == 503
    assert response.json()["error"] == code
    assert_no_leak(response)


def test_decode_failure_is_safe_400(monkeypatch, demo_env):
    # A decode error raised by an audio library maps to a client-side 400, not a 500.
    error = type("LibsndfileError", (RuntimeError,), {"__module__": "soundfile"})

    def _raise(*args, **kwargs):
        raise error("Error opening '/models/input': format not recognised.")

    monkeypatch.setattr(local_inference, "run_local_separation", _raise)
    response = separate()
    assert response.status_code == 400
    assert response.json()["error"] == "unsupported_or_corrupt_audio"
    assert_no_leak(response)


def test_unexpected_failure_is_safe_500(monkeypatch, demo_env):
    def _raise(*args, **kwargs):
        raise RuntimeError("boom at /app/local-data/demo with best_model.pt")

    monkeypatch.setattr(local_inference, "run_local_separation", _raise)
    response = separate()
    assert response.status_code == 500
    assert response.json()["error"] == "separation_failed"
    assert_no_leak(response)


def test_failed_job_leaves_no_files_behind(monkeypatch, demo_env):
    def _raise(*args, **kwargs):
        raise local_checkpoint.LocalModelConfigError("no root")

    monkeypatch.setattr(local_inference, "run_local_separation", _raise)
    separate()
    assert list(demo_env.iterdir()) == []


# --- 9. Aggregate no-leak sweep ----------------------------------------------


def test_no_demo_response_leaks_paths_or_secrets(monkeypatch, mocked_separation):
    job_id = separate().json()["jobId"]
    responses = [
        separate(),
        client.get(f"/demo/jobs/{job_id}/stems/vocals"),
        client.get(f"/demo/jobs/{uuid.uuid4()}/stems/background"),
        client.get("/demo/jobs/not-a-uuid/stems/vocals"),
        client.get(f"/demo/jobs/{job_id}/stems/drums"),
        separate(content=b""),
        separate(headers={"content-type": "text/plain"}),
    ]
    for response in responses:
        assert_no_leak(response)


# --- Demo-only boundaries -----------------------------------------------------


def test_client_filename_never_reaches_the_filesystem(mocked_separation):
    # A filename-looking header must not influence storage: the upload is stored
    # under the server-generated UUID with a fixed name.
    job_id = separate(
        headers={**WAV_HEADERS, "x-filename": "../../evil.wav"}
    ).json()["jobId"]
    job_dir = mocked_separation / job_id
    assert sorted(p.name for p in job_dir.iterdir()) == [
        "background.wav",
        "input",
        "vocals.wav",
    ]


def test_previous_job_files_are_discarded(mocked_separation):
    first = separate().json()["jobId"]
    second = separate().json()["jobId"]
    # Minimal cleanup (DEC-0009 §7): only the newest job survives.
    assert not (mocked_separation / first).exists()
    assert (mocked_separation / second).exists()
    assert client.get(f"/demo/jobs/{first}/stems/vocals").status_code == 404
