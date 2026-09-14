"""Subscription management — Pro tier upgrade via payment or coupon."""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.auth import current_user, get_db
from app.db.models import Coupon, CouponRedemption, User

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

PRO_MONTHLY_PRICE = 29
PRO_ANNUAL_PRICE = 249
CURRENCY = "ILS"


class SubscribeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan: str
    coupon_code: str | None = Field(default=None, max_length=64)


class SubscribeResponse(BaseModel):
    message: str
    tier: str
    plan: str
    price: int
    currency: str
    via_coupon: bool = False


@router.post("/subscribe", response_model=SubscribeResponse)
def subscribe(
    payload: SubscribeRequest,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> SubscribeResponse:
    if payload.plan not in ("monthly", "annual"):
        raise HTTPException(status_code=400, detail={"error": "invalid_plan", "message": "Plan must be 'monthly' or 'annual'."})

    if user.tier == "pro":
        raise HTTPException(status_code=400, detail={"error": "already_pro", "message": "כבר יש לך מנוי Pro."})

    price = PRO_MONTHLY_PRICE if payload.plan == "monthly" else PRO_ANNUAL_PRICE

    if not payload.coupon_code:
        raise HTTPException(status_code=400, detail={"error": "coupon_required", "message": "נדרש קוד קופון לשדרוג."})

    coupon = db.scalars(
        select(Coupon).where(Coupon.code == payload.coupon_code)
    ).first()

    if coupon is None or not coupon.active:
        raise HTTPException(status_code=400, detail={"error": "invalid_coupon", "message": "קוד קופון לא תקין."})

    now = datetime.datetime.now(datetime.timezone.utc)
    if coupon.expires_at and coupon.expires_at <= now:
        raise HTTPException(status_code=400, detail={"error": "expired_coupon", "message": "קוד הקופון פג תוקף."})

    if coupon.redemption_count >= coupon.max_redemptions:
        raise HTTPException(status_code=400, detail={"error": "coupon_used", "message": "הקופון נוצל במלואו."})

    already = db.scalars(
        select(CouponRedemption).where(
            CouponRedemption.coupon_id == coupon.id,
            CouponRedemption.user_id == user.id,
        )
    ).first()
    if already:
        raise HTTPException(status_code=400, detail={"error": "already_redeemed", "message": "כבר מימשת קופון זה."})

    db.add(CouponRedemption(coupon_id=coupon.id, user_id=user.id))
    coupon.redemption_count += 1
    user.tier = "pro"
    user.subscription_expires_at = now + datetime.timedelta(days=coupon.days_valid)
    db.commit()

    return SubscribeResponse(
        message=f"הקופון הופעל! שודרגת לרמה מקצועית ל-{coupon.days_valid} ימים.",
        tier="pro",
        plan=payload.plan,
        price=0,
        currency=CURRENCY,
        via_coupon=True,
    )


@router.get("/plans")
def get_plans() -> dict:
    return {
        "plans": [
            {"id": "monthly", "name": "חודשי", "price": PRO_MONTHLY_PRICE, "currency": CURRENCY, "interval": "month"},
            {"id": "annual", "name": "שנתי", "price": PRO_ANNUAL_PRICE, "currency": CURRENCY, "interval": "year", "savings": PRO_MONTHLY_PRICE * 12 - PRO_ANNUAL_PRICE},
        ]
    }
