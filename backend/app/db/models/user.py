"""User and UserSession models."""

from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    String,
    Uuid,
    ForeignKey,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from .mixins import CreatedAtMixin, UpdatedAtMixin


class User(CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    email_opt_in: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    role: Mapped[str] = mapped_column(
        String(32), nullable=False, default="free", server_default="free"
    )
    tier: Mapped[str] = mapped_column(
        String(16), nullable=False, default="free", server_default="free"
    )
    subscription_expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    songs: Mapped[list["Song"]] = relationship(back_populates="owner")
    daily_usage: Mapped[list["DailyUsage"]] = relationship(back_populates="user")

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'blocked', 'deleted')", name="status_allowed"
        ),
        CheckConstraint(
            "role IN ('free', 'pro', 'content_moderator', 'user_admin', 'coupon_admin', 'super_admin')",
            name="role_allowed",
        ),
        CheckConstraint(
            "tier IN ('free', 'pro')",
            name="tier_allowed",
        ),
    )


class UserSession(CreatedAtMixin, Base):
    """One opaque server-side login session (P3-001; DEC-0010 D1, D2, section 3).

    Only the **SHA-256 hex of the session token** is stored — never the token
    itself, so a database leak hands over no live session.  Append-only in
    practice: a session is created at login and its row is deleted at logout or
    when it is found expired (D5), so there is no ``updated_at`` and no
    ``revoked_at`` to interpret.  Absolute 7-day lifetime, no sliding renewal.
    """

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
