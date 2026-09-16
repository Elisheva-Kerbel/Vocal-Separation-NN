"""Shared route helpers -- DRY building blocks used by multiple route modules."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.constants import VALID_PURPOSES, Visibility
from app.db.models import AudioFile, Song


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"error": code, "message": message})


def get_audio_file_or_404(db: DbSession, song_id, purpose: str) -> AudioFile:
    audio_file = db.scalars(
        select(AudioFile).where(
            AudioFile.song_id == song_id,
            AudioFile.purpose == purpose,
        )
    ).first()
    if audio_file is None:
        raise api_error(404, "stem_not_found", "Stem not available.")
    return audio_file


def validate_purpose(purpose: str) -> None:
    if purpose not in VALID_PURPOSES:
        raise api_error(400, "invalid_purpose", "Purpose must be vocals, background, or original.")


def get_public_song_or_404(db: DbSession, song_id) -> Song:
    song = db.get(Song, song_id)
    if song is None or song.visibility != Visibility.PUBLIC or song.deleted_at is not None:
        raise api_error(404, "not_found", "Song not found.")
    return song
