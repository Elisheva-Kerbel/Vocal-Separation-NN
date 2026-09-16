"""Song, AudioFile and SeparationJob models."""

from __future__ import annotations

import datetime
import decimal
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from .mixins import CreatedAtMixin, UpdatedAtMixin


class Song(CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "songs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="uploaded", index=True
    )
    visibility: Mapped[str] = mapped_column(
        String(16), nullable=False, default="private", server_default="private"
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rights_confirmed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )

    owner: Mapped["User"] = relationship(back_populates="songs")
    audio_files: Mapped[list["AudioFile"]] = relationship(back_populates="song")
    separation_jobs: Mapped[list["SeparationJob"]] = relationship(
        back_populates="song"
    )
    song_tags: Mapped[list["SongTag"]] = relationship(back_populates="song")
    ratings: Mapped[list["Rating"]] = relationship(back_populates="song")

    __table_args__ = (
        CheckConstraint(
            "status IN ('uploaded', 'processing', 'ready', 'failed')",
            name="status_allowed",
        ),
        CheckConstraint(
            "visibility IN ('private', 'public')",
            name="visibility_allowed",
        ),
        Index("ix_songs_user_id", "user_id", "created_at"),
    )


class AudioFile(CreatedAtMixin, UpdatedAtMixin, Base):
    """A stored audio object's metadata (DEC-0006 section 4.3, section 5).  Sole owner of
    ``storage_key``.  The DB holds metadata only — never audio bytes."""

    __tablename__ = "audio_files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    song_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("songs.id"), nullable=False, index=True
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_seconds: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric, nullable=True
    )
    original_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)

    song: Mapped["Song"] = relationship(back_populates="audio_files")

    __table_args__ = (
        CheckConstraint(
            "purpose IN ('original', 'vocals', 'background')", name="purpose_allowed"
        ),
        UniqueConstraint("song_id", "purpose"),
    )


class SeparationJob(CreatedAtMixin, UpdatedAtMixin, Base):
    """An async separation run for a song (DEC-0006 section 4.4).  ``model_tier`` is a
    logical enum only — never a checkpoint/model/local path, no LOCAL_MODEL_ROOT.
    ``error_message`` must not carry paths, secrets or DATABASE_URL."""

    __tablename__ = "separation_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    song_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("songs.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="queued", index=True
    )
    model_tier: Mapped[str | None] = mapped_column(String(32), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    started_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    song: Mapped["Song"] = relationship(back_populates="separation_jobs")

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed', 'canceled')",
            name="status_allowed",
        ),
        CheckConstraint("model_tier IN ('basic', 'professional')", name="model_tier_allowed"),
        Index("ix_separation_jobs_song_id", "song_id", "created_at"),
    )
