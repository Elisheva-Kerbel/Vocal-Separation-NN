"""Social models: Tag, SongTag, Rating, ContentReport."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from .mixins import CreatedAtMixin, UpdatedAtMixin


class Tag(CreatedAtMixin, UpdatedAtMixin, Base):
    """An organisational tag (DEC-0006 section 4.5).  Default values are seeded in P2-004."""

    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    song_tags: Mapped[list["SongTag"]] = relationship(back_populates="tag")


class SongTag(CreatedAtMixin, Base):
    """Song-Tag association (DEC-0006 section 4.6).  Composite PK is the uniqueness --
    a tag applies to a song at most once.  Append-only (``created_at`` only)."""

    __tablename__ = "song_tags"

    song_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("songs.id"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tags.id"), primary_key=True, index=True
    )

    song: Mapped["Song"] = relationship(back_populates="song_tags")
    tag: Mapped["Tag"] = relationship(back_populates="song_tags")


class Rating(CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "ratings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    song_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("songs.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)

    song: Mapped["Song"] = relationship(back_populates="ratings")
    user: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint("song_id", "user_id"),
        CheckConstraint("score >= 1 AND score <= 5", name="score_range"),
    )


class ContentReport(CreatedAtMixin, Base):
    __tablename__ = "content_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    song_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("songs.id"), nullable=False
    )
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending"
    )
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'actioned', 'dismissed')",
            name="report_status_allowed",
        ),
    )
