"""Quota enforcement (Phase 7 / Phase 12 split)."""

from __future__ import annotations

import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.config import load_settings
from app.constants import ModelTier, UserTier
from app.db.models import DailyUsage, User

UNLIMITED_EMAILS = frozenset({
    "e0583292053@gmail.com",
})


def _is_unlimited(user: User) -> bool:
    return user.email in UNLIMITED_EMAILS


def check_quota(db: DbSession, user: User, model_choice: str = ModelTier.BASIC) -> None:
    if _is_unlimited(user):
        return
    settings = load_settings()
    today = datetime.date.today()
    daily = db.scalars(
        select(DailyUsage).where(
            DailyUsage.user_id == user.id,
            DailyUsage.usage_date == today,
        )
    ).first()

    if model_choice == ModelTier.PROFESSIONAL:
        if user.tier != UserTier.PRO:
            raise HTTPException(
                status_code=403,
                detail={"error": "pro_required", "message": "Professional separations require a Pro subscription."},
            )
        used = daily.professional_count if daily else 0
        limit = settings.pro_daily_limit
        if used >= limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "quota_exceeded",
                    "message": f"Daily professional limit reached ({limit}/day). Try again tomorrow.",
                    "used": used,
                    "limit": limit,
                },
            )
    else:
        if user.tier == UserTier.PRO:
            return
        used = daily.basic_count if daily else 0
        limit = settings.free_daily_limit
        if used >= limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "quota_exceeded",
                    "message": f"Daily basic limit reached ({limit}/day). Try again tomorrow.",
                    "used": used,
                    "limit": limit,
                },
            )


def get_usage_info(db: DbSession, user: User) -> dict:
    settings = load_settings()
    today = datetime.date.today()
    daily = db.scalars(
        select(DailyUsage).where(
            DailyUsage.user_id == user.id,
            DailyUsage.usage_date == today,
        )
    ).first()

    basic_used = daily.basic_count if daily else 0
    pro_used = daily.professional_count if daily else 0

    if _is_unlimited(user):
        return {
            "tier": user.tier,
            "basic_used": basic_used,
            "basic_limit": None,
            "professional_used": pro_used,
            "professional_limit": None,
        }
    if user.tier == UserTier.PRO:
        return {
            "tier": user.tier,
            "basic_used": basic_used,
            "basic_limit": None,
            "professional_used": pro_used,
            "professional_limit": settings.pro_daily_limit,
        }
    return {
        "tier": user.tier,
        "basic_used": basic_used,
        "basic_limit": settings.free_daily_limit,
        "professional_used": 0,
        "professional_limit": 0,
    }
