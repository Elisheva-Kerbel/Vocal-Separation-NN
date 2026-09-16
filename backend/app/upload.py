"""Upload API (Phase 4) -- authenticated file upload to private storage."""

from __future__ import annotations

import hashlib
import os
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session as DbSession

from app.auth import current_user, get_db
from app.config import load_settings
from app.constants import (
    MAX_TITLE_LENGTH,
    AudioPurpose,
    JobStatus,
    ModelTier,
    SongStatus,
    Visibility,
)
from app.db.models import AudioFile, SeparationJob, Song, User
from app.helpers import api_error
from app.quotas import check_quota

router = APIRouter(tags=["upload"])

ACCEPTED_TYPES = {
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/m4a": ".m4a",
}


class UploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    song_id: uuid.UUID
    status: str
    title: str | None
    model_tier: str


@router.post("/upload", status_code=201, response_model=UploadResponse)
async def upload_song(
    file: UploadFile = File(...),
    model_choice: str = Form("basic"),
    visibility: str = Form("private"),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> UploadResponse:
    from app import storage
    from app.tasks import run_separation

    settings = load_settings()

    if model_choice not in (ModelTier.BASIC, ModelTier.PROFESSIONAL):
        raise api_error(400, "invalid_model_choice", "Model choice must be 'basic' or 'professional'.")
    if visibility not in (Visibility.PRIVATE, Visibility.PUBLIC):
        raise api_error(400, "invalid_visibility", "Visibility must be 'private' or 'public'.")

    content_type = (file.content_type or "application/octet-stream").split(";")[0].strip().lower()
    if content_type not in ACCEPTED_TYPES:
        raise api_error(415, "unsupported_format", "Upload MP3, WAV, or M4A.")

    data = await file.read()
    if len(data) == 0:
        raise api_error(400, "empty_file", "The uploaded file is empty.")
    if len(data) > settings.max_upload_bytes:
        raise api_error(413, "file_too_large", f"Max {settings.max_upload_bytes // (1024*1024)} MB.")

    model_tier = ModelTier.PROFESSIONAL if model_choice == ModelTier.PROFESSIONAL else ModelTier.BASIC
    check_quota(db, user, model_tier)

    ext = ACCEPTED_TYPES[content_type]
    song_id = uuid.uuid4()
    storage_key = storage.generate_storage_key(user.id, song_id, AudioPurpose.ORIGINAL, ext)

    title = file.filename or None
    if title:
        title = os.path.splitext(title)[0][:MAX_TITLE_LENGTH]

    checksum = hashlib.sha256(data).hexdigest()

    try:
        storage.ensure_bucket()
        storage.upload_bytes(data, storage_key, content_type)
    except Exception:
        raise api_error(500, "upload_failed", "Upload failed. Try again.")

    song = Song(id=song_id, user_id=user.id, title=title, status=SongStatus.UPLOADED, visibility=visibility)
    db.add(song)
    db.flush()

    audio_file = AudioFile(
        song_id=song_id,
        purpose=AudioPurpose.ORIGINAL,
        storage_key=storage_key,
        content_type=content_type,
        byte_size=len(data),
        checksum_sha256=checksum,
        original_filename=file.filename,
    )
    db.add(audio_file)

    job = SeparationJob(song_id=song_id, status=JobStatus.QUEUED, model_tier=model_tier)
    db.add(job)
    db.flush()

    song.status = SongStatus.PROCESSING
    db.commit()

    run_separation.delay(
        str(job.id), str(song_id), str(user.id), storage_key, model_tier,
    )

    return UploadResponse(id=job.id, song_id=song_id, status=SongStatus.PROCESSING, title=title, model_tier=model_tier)
