"""Billing / usage models: UsageEvent, DailyUsage, Coupon, CouponRedemption."""

from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from .mixins import CreatedAtMixin, UpdatedAtMixin


class UsageEvent(CreatedAtMixin, Base):
    """Append-only billable-usage ledger (DEC-0006 section 4.7, section 8)."""

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
    basic_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    professional_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    user: Mapped["User"] = relationship(back_populates="daily_usage")

    __table_args__ = (UniqueConstraint("user_id", "usage_date"),)


class Coupon(CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "coupons"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    tier_grant: Mapped[str] = mapped_column(String(16), nullable=False, default="pro")
    days_valid: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    max_redemptions: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    redemption_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    redemptions: Mapped[list["CouponRedemption"]] = relationship(back_populates="coupon")


class CouponRedemption(CreatedAtMixin, Base):
    __tablename__ = "coupon_redemptions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    coupon_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("coupons.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    coupon: Mapped["Coupon"] = relationship(back_populates="redemptions")
    user: Mapped["User"] = relationship()

    __table_args__ = (UniqueConstraint("coupon_id", "user_id"),)
