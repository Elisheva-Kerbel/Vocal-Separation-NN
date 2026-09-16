"""Public Library routes (Phase 9) -- discovery, publish/unpublish, ratings, reports."""

from __future__ import annotations

import datetime
import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.auth import current_user, get_db
from app.constants import (
    STEM_OUTPUT_CONTENT_TYPE,
    ReportStatus,
    SongStatus,
    Visibility,
)
from app.db.models import AudioFile, ContentReport, Rating, Song, User
from app.helpers import api_error, get_audio_file_or_404, get_public_song_or_404, validate_purpose

router = APIRouter(prefix="/public", tags=["public"])


class PublicSong(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    title: str | None
    status: str
    created_at: datetime.datetime
    owner_name: str | None
    avg_rating: float | None
    rating_count: int


class PublicListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    songs: list[PublicSong]
    total: int


class RateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=1, le=5)


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(max_length=256)


class PublishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rights_confirmed: bool


@router.get("/songs", response_model=PublicListResponse)
def public_library(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: DbSession = Depends(get_db),
) -> PublicListResponse:
    base = (
        select(Song)
        .where(Song.visibility == Visibility.PUBLIC, Song.status == SongStatus.READY, Song.deleted_at.is_(None))
    )
    total = len(db.scalars(select(Song.id).where(
        Song.visibility == Visibility.PUBLIC, Song.status == SongStatus.READY, Song.deleted_at.is_(None)
    )).all())

    songs = db.scalars(base.order_by(Song.created_at.desc()).offset(offset).limit(limit)).all()

    result = []
    for s in songs:
        avg = db.scalar(select(func.avg(Rating.score)).where(Rating.song_id == s.id))
        count = db.scalar(select(func.count(Rating.id)).where(Rating.song_id == s.id)) or 0

        owner_name = s.owner.email.split("@")[0] if s.owner else None

        result.append(PublicSong(
            id=s.id, title=s.title, status=s.status, created_at=s.created_at,
            owner_name=owner_name, avg_rating=round(float(avg), 1) if avg else None,
            rating_count=count,
        ))

    return PublicListResponse(songs=result, total=total)


@router.get("/songs/{song_id}", response_model=PublicSong)
def public_song(song_id: uuid.UUID, db: DbSession = Depends(get_db)) -> PublicSong:
    song = get_public_song_or_404(db, song_id)

    avg = db.scalar(select(func.avg(Rating.score)).where(Rating.song_id == song_id))
    count = db.scalar(select(func.count(Rating.id)).where(Rating.song_id == song_id)) or 0

    owner_name = song.owner.email.split("@")[0] if song.owner else None

    return PublicSong(
        id=song.id, title=song.title, status=song.status, created_at=song.created_at,
        owner_name=owner_name, avg_rating=round(float(avg), 1) if avg else None,
        rating_count=count,
    )


@router.get("/songs/{song_id}/listen-url/{purpose}")
def public_listen_url(
    song_id: uuid.UUID,
    purpose: str,
    db: DbSession = Depends(get_db),
):
    from app import storage
    from app.config import load_settings

    validate_purpose(purpose)
    get_public_song_or_404(db, song_id)
    audio_file = get_audio_file_or_404(db, song_id, purpose)

    settings = load_settings()
    ttl = settings.signed_url_listen_ttl
    url = storage.generate_signed_url(audio_file.storage_key, ttl)
    return {"url": url, "expires_in": ttl, "purpose": purpose}


@router.get("/songs/{song_id}/stream/{purpose}")
def public_stream(
    song_id: uuid.UUID,
    purpose: str,
    db: DbSession = Depends(get_db),
):
    from io import BytesIO

    from app import storage

    validate_purpose(purpose)
    get_public_song_or_404(db, song_id)
    audio_file = get_audio_file_or_404(db, song_id, purpose)

    data = storage.download_bytes(audio_file.storage_key)
    content_type = audio_file.content_type or STEM_OUTPUT_CONTENT_TYPE
    return StreamingResponse(
        BytesIO(data),
        media_type=content_type,
        headers={"Content-Length": str(len(data))},
    )


@router.post("/songs/{song_id}/publish")
def publish_song(
    song_id: uuid.UUID,
    payload: PublishRequest,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    song = db.get(Song, song_id)
    if song is None or song.user_id != user.id or song.deleted_at is not None:
        raise api_error(404, "not_found", "Song not found.")
    if song.status != SongStatus.READY:
        raise api_error(400, "not_ready", "Song must be ready before publishing.")
    if not payload.rights_confirmed:
        raise api_error(400, "rights_required", "You must confirm you have the rights.")

    song.visibility = Visibility.PUBLIC
    song.rights_confirmed = True
    db.commit()

    from app.tasks import send_new_song_emails
    owner_name = user.email.split("@")[0]
    send_new_song_emails.delay(song.title or "ללא שם", owner_name)

    return {"message": "Song published."}


@router.post("/songs/{song_id}/unpublish")
def unpublish_song(
    song_id: uuid.UUID,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    song = db.get(Song, song_id)
    if song is None or song.user_id != user.id or song.deleted_at is not None:
        raise api_error(404, "not_found", "Song not found.")

    song.visibility = Visibility.PRIVATE
    db.commit()
    return {"message": "Song unpublished."}


@router.post("/songs/{song_id}/rate")
def rate_song(
    song_id: uuid.UUID,
    payload: RateRequest,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    song = get_public_song_or_404(db, song_id)
    if song.user_id == user.id:
        raise api_error(400, "self_rating", "You cannot rate your own song.")

    existing = db.scalars(
        select(Rating).where(Rating.song_id == song_id, Rating.user_id == user.id)
    ).first()
    if existing:
        existing.score = payload.score
    else:
        db.add(Rating(song_id=song_id, user_id=user.id, score=payload.score))
    db.commit()
    return {"message": "Rating saved."}


@router.post("/songs/{song_id}/report")
def report_song(
    song_id: uuid.UUID,
    payload: ReportRequest,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    get_public_song_or_404(db, song_id)

    db.add(ContentReport(song_id=song_id, reporter_id=user.id, reason=payload.reason))
    db.commit()
    return {"message": "Report submitted."}
