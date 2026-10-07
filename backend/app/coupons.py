"""Coupon redemption (Phase 7)."""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.auth import current_user, get_db
from app.constants import UserTier
from app.db.models import Coupon, CouponRedemption, User

router = APIRouter(prefix="/coupons", tags=["coupons"])


class RedeemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(max_length=64)


@router.post("/redeem")
def redeem_coupon(
    payload: RedeemRequest,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    coupon = db.scalars(
        select(Coupon).where(Coupon.code == payload.code)
    ).first()

    if coupon is None or not coupon.active:
        raise HTTPException(status_code=400, detail={"error": "invalid_coupon", "message": "Invalid or inactive coupon."})

    now = datetime.datetime.now(datetime.timezone.utc)
    if coupon.expires_at and coupon.expires_at <= now:
        raise HTTPException(status_code=400, detail={"error": "expired_coupon", "message": "This coupon has expired."})

    if coupon.redemption_count >= coupon.max_redemptions:
        raise HTTPException(status_code=400, detail={"error": "coupon_used", "message": "This coupon has been fully redeemed."})

    already = db.scalars(
        select(CouponRedemption).where(
            CouponRedemption.coupon_id == coupon.id,
            CouponRedemption.user_id == user.id,
        )
    ).first()
    if already:
        raise HTTPException(status_code=400, detail={"error": "already_redeemed", "message": "You already redeemed this coupon."})

    db.add(CouponRedemption(coupon_id=coupon.id, user_id=user.id))
    coupon.redemption_count += 1

    if coupon.tier_grant == UserTier.PRO:
        user.tier = UserTier.PRO

    db.commit()
    return {"message": f"Coupon redeemed. You now have {coupon.tier_grant} tier."}
