"""Song and result routes (Phase 6)."""

from __future__ import annotations

import datetime
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.auth import current_user, get_db
from app.config import load_settings
from app.constants import (
    STEM_OUTPUT_CONTENT_TYPE,
    MAX_TITLE_LENGTH,
    GrantType,
    Visibility,
)
from app.db.models import AudioFile, SeparationJob, SignedUrlGrant, Song, User
from app.helpers import api_error, get_audio_file_or_404, validate_purpose

router = APIRouter(prefix="/songs", tags=["songs"])


class SongDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    title: str | None
    status: str
    visibility: str
    created_at: datetime.datetime
    stems: list[StemInfo]
    job: JobInfo | None


class StemInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    purpose: str
    content_type: str
    byte_size: int


class JobInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    status: str
    model_tier: str | None
    error_message: str | None
    started_at: datetime.datetime | None
    finished_at: datetime.datetime | None


class SignedUrlResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str
    expires_in: int
    purpose: str


def _get_song_or_404(db: DbSession, song_id: uuid.UUID) -> Song:
    song = db.get(Song, song_id)
    if song is None or song.deleted_at is not None:
        raise api_error(404, "song_not_found", "Song not found.")
    return song


def _check_access(song: Song, user: User) -> None:
    if song.user_id != user.id and song.visibility != Visibility.PUBLIC:
        raise api_error(403, "forbidden", "You do not have access to this song.")


@router.get("/{song_id}", response_model=SongDetail)
def get_song(
    song_id: uuid.UUID,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> SongDetail:
    song = _get_song_or_404(db, song_id)
    _check_access(song, user)

    stems = [
        StemInfo(purpose=af.purpose, content_type=af.content_type, byte_size=af.byte_size)
        for af in song.audio_files
    ]

    latest_job = db.scalars(
        select(SeparationJob)
        .where(SeparationJob.song_id == song_id)
        .order_by(SeparationJob.created_at.desc())
    ).first()

    job_info = None
    if latest_job:
        job_info = JobInfo(
            id=latest_job.id,
            status=latest_job.status,
            model_tier=latest_job.model_tier,
            error_message=latest_job.error_message,
            started_at=latest_job.started_at,
            finished_at=latest_job.finished_at,
        )

    return SongDetail(
        id=song.id,
        title=song.title,
        status=song.status,
        visibility=song.visibility,
        created_at=song.created_at,
        stems=stems,
        job=job_info,
    )


@router.get("/{song_id}/status")
def get_song_status(
    song_id: uuid.UUID,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    song = _get_song_or_404(db, song_id)
    _check_access(song, user)
    return {"id": str(song.id), "status": song.status}


@router.get("/{song_id}/listen-url/{purpose}", response_model=SignedUrlResponse)
def get_listen_url(
    song_id: uuid.UUID,
    purpose: str,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> SignedUrlResponse:
    from app import storage

    validate_purpose(purpose)
    song = _get_song_or_404(db, song_id)
    _check_access(song, user)
    audio_file = get_audio_file_or_404(db, song_id, purpose)

    settings = load_settings()
    ttl = settings.signed_url_listen_ttl
    url = storage.generate_signed_url(audio_file.storage_key, ttl)

    grant = SignedUrlGrant(
        audio_file_id=audio_file.id,
        user_id=user.id,
        grant_type=GrantType.LISTEN,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=ttl),
    )
    db.add(grant)
    db.commit()

    return SignedUrlResponse(url=url, expires_in=ttl, purpose=purpose)


@router.get("/{song_id}/download-url/{purpose}", response_model=SignedUrlResponse)
def get_download_url(
    song_id: uuid.UUID,
    purpose: str,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> SignedUrlResponse:
    from app import storage

    validate_purpose(purpose)
    song = _get_song_or_404(db, song_id)
    _check_access(song, user)
    audio_file = get_audio_file_or_404(db, song_id, purpose)

    settings = load_settings()
    ttl = settings.signed_url_download_ttl
    filename = f"{song.title or 'track'}_{purpose}.wav"
    url = storage.generate_signed_url(audio_file.storage_key, ttl, download_filename=filename)

    grant = SignedUrlGrant(
        audio_file_id=audio_file.id,
        user_id=user.id,
        grant_type=GrantType.DOWNLOAD,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=ttl),
    )
    db.add(grant)
    db.commit()

    return SignedUrlResponse(url=url, expires_in=ttl, purpose=purpose)


@router.get("/{song_id}/stream/{purpose}")
def stream_audio(
    song_id: uuid.UUID,
    purpose: str,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
):
    from io import BytesIO

    from app import storage

    validate_purpose(purpose)
    song = _get_song_or_404(db, song_id)
    _check_access(song, user)
    audio_file = get_audio_file_or_404(db, song_id, purpose)

    data = storage.download_bytes(audio_file.storage_key)
    content_type = audio_file.content_type or STEM_OUTPUT_CONTENT_TYPE
    return StreamingResponse(
        BytesIO(data),
        media_type=content_type,
        headers={
            "Content-Length": str(len(data)),
            "Accept-Ranges": "bytes",
        },
    )


class RenameSongRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str


@router.patch("/{song_id}")
def rename_song(
    song_id: uuid.UUID,
    payload: RenameSongRequest,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    song = _get_song_or_404(db, song_id)
    if song.user_id != user.id:
        raise api_error(403, "forbidden", "You do not have access to this song.")
    song.title = payload.title[:MAX_TITLE_LENGTH]
    db.commit()
    return {"title": song.title}
