"""My Library routes (Phase 8) — personal song history and soft delete."""

from __future__ import annotations

import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.auth import current_user, get_db
from app.db.models import SeparationJob, Song, User

router = APIRouter(prefix="/library", tags=["library"])


class LibrarySong(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    title: str | None
    status: str
    visibility: str
    created_at: datetime.datetime
    model_tier: str | None = None


class LibraryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    songs: list[LibrarySong]
    total: int


@router.get("", response_model=LibraryResponse)
def my_library(
    status: str | None = Query(None),
    visibility: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> LibraryResponse:
    q = select(Song).where(Song.user_id == user.id, Song.deleted_at.is_(None))

    if status:
        q = q.where(Song.status == status)
    if visibility:
        q = q.where(Song.visibility == visibility)

    total_q = select(Song.id).where(Song.user_id == user.id, Song.deleted_at.is_(None))
    if status:
        total_q = total_q.where(Song.status == status)
    if visibility:
        total_q = total_q.where(Song.visibility == visibility)

    total = len(db.scalars(total_q).all())

    songs = db.scalars(
        q.order_by(Song.created_at.desc()).offset(offset).limit(limit)
    ).all()

    song_ids = [s.id for s in songs]
    tier_map = {}
    if song_ids:
        jobs = db.scalars(
            select(SeparationJob).where(SeparationJob.song_id.in_(song_ids))
        ).all()
        for j in jobs:
            tier_map[j.song_id] = j.model_tier

    return LibraryResponse(
        songs=[
            LibrarySong(
                id=s.id,
                title=s.title,
                status=s.status,
                visibility=s.visibility,
                created_at=s.created_at,
                model_tier=tier_map.get(s.id),
            )
            for s in songs
        ],
        total=total,
    )


@router.delete("/{song_id}", status_code=200)
def delete_song(
    song_id: uuid.UUID,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    song = db.get(Song, song_id)
    if song is None or song.user_id != user.id:
        raise HTTPException(
            status_code=404,
            detail={"error": "song_not_found", "message": "Song not found."},
        )
    if song.deleted_at is not None:
        return {"message": "Already deleted."}

    song.deleted_at = datetime.datetime.now(datetime.timezone.utc)
    song.visibility = "private"
    db.commit()
    return {"message": "Song deleted."}
