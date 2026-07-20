"""Phase 2 core domain models (P2-002).

The 8 core SQLAlchemy entities defined by ``docs/decisions/DEC-0006`` — the upload →
async separation → private result metadata → usage-tracking core, plus tag
organisation. Sync SQLAlchemy 2.x on the single shared ``Base``/``MetaData`` from
P2-001 (DEC-0005); no new base, no second metadata, no async, and importing this
module opens no database connection.

Deferred entities (Rating, Coupon, CouponRedemption, SignedUrlGrant, ContentReport,
AdminAuditEvent) are NOT defined here — their contract is fixed in DEC-0006 but their
tables are created in their approved phase (DEC-0006 §2/§12).

Security (DEC-0006 §5–§7): no audio bytes / LargeBinary / BYTEA, no base64 audio, no
checkpoint/model/local filesystem path columns, no LOCAL_MODEL_ROOT, no signed-URL
string columns, no public-URL columns. ``storage_key`` lives only on ``AudioFile`` as
an internal key and is never exposed in an API/client schema (no schemas exist in
P2-002). ``model_tier`` is a logical enum only, never a path.
"""

from __future__ import annotations

import datetime
import decimal
import uuid

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# Timestamp columns are UTC-aware (DEC-0006 §3). Two flat mixins (no hierarchy):
# every table carries ``created_at``; mutable tables also carry ``updated_at``.
# DEC-0005 §5 permits a timestamp mixin once models are actually designed — this is
# that point, and it keeps the tz-aware column definition from being duplicated.
class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class User(CreatedAtMixin, UpdatedAtMixin, Base):
    """A registered account (DEC-0006 §4.1). Owner of songs and usage.

    No password/auth-credential columns in P2 — authentication is Phase 3.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    songs: Mapped[list["Song"]] = relationship(back_populates="owner")
    daily_usage: Mapped[list["DailyUsage"]] = relationship(back_populates="user")

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'blocked', 'deleted')", name="status_allowed"
        ),
    )


class Song(CreatedAtMixin, UpdatedAtMixin, Base):
    """A logical uploaded track (DEC-0006 §4.2). One owner; the container for its
    audio files and separation jobs. No storage reference and no public/visibility
    column — everything is private in Phase 2."""

    __tablename__ = "songs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="uploaded", index=True
    )

    owner: Mapped["User"] = relationship(back_populates="songs")
    audio_files: Mapped[list["AudioFile"]] = relationship(back_populates="song")
    separation_jobs: Mapped[list["SeparationJob"]] = relationship(
        back_populates="song"
    )
    song_tags: Mapped[list["SongTag"]] = relationship(back_populates="song")

    __table_args__ = (
        CheckConstraint(
            "status IN ('uploaded', 'processing', 'ready', 'failed')",
            name="status_allowed",
        ),
        Index("ix_songs_user_id", "user_id", "created_at"),
    )


class AudioFile(CreatedAtMixin, UpdatedAtMixin, Base):
    """A stored audio object's metadata (DEC-0006 §4.3, §5). Sole owner of
    ``storage_key``. The DB holds metadata only — never audio bytes."""

    __tablename__ = "audio_files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    song_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("songs.id"), nullable=False, index=True
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    # Internal, opaque storage key. Internal-only; never exposed in an API/client
    # schema (P2-003). No bucket/provider column (resolved from config at access
    # time), no public URL, no signed URL, no local filesystem path.
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
    """An async separation run for a song (DEC-0006 §4.4). ``model_tier`` is a
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
        CheckConstraint("model_tier IN ('basic')", name="model_tier_allowed"),
        Index("ix_separation_jobs_song_id", "song_id", "created_at"),
    )


class Tag(CreatedAtMixin, UpdatedAtMixin, Base):
    """An organisational tag (DEC-0006 §4.5). Default values are seeded in P2-004."""

    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    song_tags: Mapped[list["SongTag"]] = relationship(back_populates="tag")


class SongTag(CreatedAtMixin, Base):
    """Song↔Tag association (DEC-0006 §4.6). Composite PK is the uniqueness —
    a tag applies to a song at most once. Append-only (``created_at`` only)."""

    __tablename__ = "song_tags"

    song_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("songs.id"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tags.id"), primary_key=True, index=True
    )

    song: Mapped["Song"] = relationship(back_populates="song_tags")
    tag: Mapped["Tag"] = relationship(back_populates="song_tags")


class UsageEvent(CreatedAtMixin, Base):
    """Append-only billable-usage ledger (DEC-0006 §4.7, §8). Idempotency key
    ``(song_id, event_type)`` — at most one ``separation_succeeded`` per song
    (guards R-006). Written only when a job succeeds and the song is ready
    (R-005); the finalise logic lands in P5/P7. Append-only (``created_at`` only)."""

    __tablename__ = "usage_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    song_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("songs.id"), nullable=False
    )
    separation_job_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("separation_jobs.id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)

    user: Mapped["User"] = relationship()
    song: Mapped["Song"] = relationship()
    separation_job: Mapped["SeparationJob | None"] = relationship()

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('separation_succeeded')", name="event_type_allowed"
        ),
        UniqueConstraint("song_id", "event_type"),
        Index("ix_usage_events_user_id", "user_id", "created_at"),
    )


class DailyUsage(CreatedAtMixin, UpdatedAtMixin, Base):
    """Per-user-per-day usage aggregate (DEC-0006 §4.8, §8). One row per user per
    UTC day; ``successful_count`` is a rollup derived from the UsageEvent ledger."""

    __tablename__ = "daily_usage"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    usage_date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, index=True
    )
    successful_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    user: Mapped["User"] = relationship(back_populates="daily_usage")

    __table_args__ = (UniqueConstraint("user_id", "usage_date"),)
