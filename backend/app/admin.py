"""Admin RBAC + Audit routes (Phase 10)."""

from __future__ import annotations

import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.auth import current_user, get_db
from app.db.models import (
    AdminAuditEvent,
    ContentReport,
    Coupon,
    Song,
    User,
)

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_ROLES = {"content_moderator", "user_admin", "coupon_admin", "super_admin"}


def _require_admin(user: User, allowed_roles: set[str] | None = None) -> None:
    if user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail={"error": "forbidden", "message": "Admin access required."})
    if allowed_roles and user.role not in allowed_roles and user.role != "super_admin":
        raise HTTPException(status_code=403, detail={"error": "forbidden", "message": "Insufficient permissions."})


def _audit(db: DbSession, admin: User, action: str, target_type: str, target_id: str, detail: str | None = None) -> None:
    db.add(AdminAuditEvent(
        admin_id=admin.id, action=action,
        target_type=target_type, target_id=target_id, detail=detail,
    ))


class UserAdminView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    email: str
    status: str
    role: str
    tier: str
    created_at: datetime.datetime


class CouponCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(max_length=64)
    tier_grant: str = "pro"
    days_valid: int = Field(default=30, ge=1)
    max_redemptions: int = Field(default=1, ge=1)
    expires_at: datetime.datetime | None = None


class CouponView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    code: str
    tier_grant: str
    days_valid: int
    max_redemptions: int
    redemption_count: int
    active: bool
    expires_at: datetime.datetime | None


class ReportView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    song_id: uuid.UUID
    reporter_id: uuid.UUID
    reason: str
    status: str
    created_at: datetime.datetime


# --- User Admin ---

@router.get("/users", response_model=list[UserAdminView])
def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> list[UserAdminView]:
    _require_admin(user, {"user_admin"})
    users = db.scalars(select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)).all()
    return [UserAdminView(id=u.id, email=u.email, status=u.status, role=u.role, tier=u.tier, created_at=u.created_at) for u in users]


@router.post("/users/{user_id}/block")
def block_user(
    user_id: uuid.UUID,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    _require_admin(user, {"user_admin"})
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "User not found."})
    target.status = "blocked"
    _audit(db, user, "block_user", "user", str(user_id))
    db.commit()
    return {"message": "User blocked."}


@router.post("/users/{user_id}/unblock")
def unblock_user(
    user_id: uuid.UUID,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    _require_admin(user, {"user_admin"})
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "User not found."})
    target.status = "active"
    _audit(db, user, "unblock_user", "user", str(user_id))
    db.commit()
    return {"message": "User unblocked."}


# --- Content Moderation ---

@router.get("/reports", response_model=list[ReportView])
def list_reports(
    status: str = Query("pending"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> list[ReportView]:
    _require_admin(user, {"content_moderator"})
    reports = db.scalars(
        select(ContentReport).where(ContentReport.status == status)
        .order_by(ContentReport.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return [ReportView(id=r.id, song_id=r.song_id, reporter_id=r.reporter_id,
                        reason=r.reason, status=r.status, created_at=r.created_at) for r in reports]


@router.post("/reports/{report_id}/action")
def action_report(
    report_id: uuid.UUID,
    action: str = Query(...),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    _require_admin(user, {"content_moderator"})
    report = db.get(ContentReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Report not found."})

    if action == "remove":
        song = db.get(Song, report.song_id)
        if song:
            song.visibility = "private"
            song.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        report.status = "actioned"
        report.resolved_by = user.id
        _audit(db, user, "remove_song", "song", str(report.song_id), f"Report {report_id}")
    elif action == "dismiss":
        report.status = "dismissed"
        report.resolved_by = user.id
        _audit(db, user, "dismiss_report", "report", str(report_id))
    else:
        raise HTTPException(status_code=400, detail={"error": "invalid_action", "message": "Action must be 'remove' or 'dismiss'."})

    db.commit()
    return {"message": f"Report {action}ed."}


# --- Coupon Admin ---

@router.get("/coupons", response_model=list[CouponView])
def list_coupons(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> list[CouponView]:
    _require_admin(user, {"coupon_admin"})
    coupons = db.scalars(select(Coupon).order_by(Coupon.created_at.desc()).offset(offset).limit(limit)).all()
    return [CouponView(id=c.id, code=c.code, tier_grant=c.tier_grant, days_valid=c.days_valid,
                         max_redemptions=c.max_redemptions, redemption_count=c.redemption_count,
                         active=c.active, expires_at=c.expires_at) for c in coupons]


@router.post("/coupons", status_code=201, response_model=CouponView)
def create_coupon(
    payload: CouponCreate,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> CouponView:
    _require_admin(user, {"coupon_admin"})
    coupon = Coupon(
        code=payload.code, tier_grant=payload.tier_grant,
        days_valid=payload.days_valid, max_redemptions=payload.max_redemptions,
        expires_at=payload.expires_at,
    )
    db.add(coupon)
    _audit(db, user, "create_coupon", "coupon", payload.code)
    db.commit()
    db.refresh(coupon)
    return CouponView(id=coupon.id, code=coupon.code, tier_grant=coupon.tier_grant,
                       days_valid=coupon.days_valid, max_redemptions=coupon.max_redemptions,
                       redemption_count=coupon.redemption_count, active=coupon.active,
                       expires_at=coupon.expires_at)


@router.post("/coupons/{coupon_id}/deactivate")
def deactivate_coupon(
    coupon_id: uuid.UUID,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    _require_admin(user, {"coupon_admin"})
    coupon = db.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Coupon not found."})
    coupon.active = False
    _audit(db, user, "deactivate_coupon", "coupon", coupon.code)
    db.commit()
    return {"message": "Coupon deactivated."}


# --- Dashboard Stats ---

@router.get("/stats")
def get_stats(
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    _require_admin(user)
    total_users = db.scalar(select(func.count(User.id))) or 0
    active_users = db.scalar(select(func.count(User.id)).where(User.status == "active")) or 0
    total_songs = db.scalar(select(func.count(Song.id)).where(Song.deleted_at.is_(None))) or 0
    public_songs = db.scalar(select(func.count(Song.id)).where(Song.visibility == "public", Song.deleted_at.is_(None))) or 0
    ready_songs = db.scalar(select(func.count(Song.id)).where(Song.status == "ready", Song.deleted_at.is_(None))) or 0
    processing_songs = db.scalar(select(func.count(Song.id)).where(Song.status.in_(["processing", "queued", "uploaded"]), Song.deleted_at.is_(None))) or 0
    failed_songs = db.scalar(select(func.count(Song.id)).where(Song.status == "failed", Song.deleted_at.is_(None))) or 0
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_songs": total_songs,
        "public_songs": public_songs,
        "ready_songs": ready_songs,
        "processing_songs": processing_songs,
        "failed_songs": failed_songs,
    }


@router.get("/all-songs")
def list_all_songs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> list[dict]:
    _require_admin(user)
    songs = db.scalars(
        select(Song).where(Song.deleted_at.is_(None))
        .order_by(Song.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return [
        {"id": str(s.id), "title": s.title, "status": s.status,
         "visibility": s.visibility, "model_tier": s.model_tier,
         "owner_email": s.owner.email if s.owner else None,
         "created_at": s.created_at.isoformat()}
        for s in songs
    ]


# --- Audit Log ---

@router.get("/audit")
def get_audit_log(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> list[dict]:
    _require_admin(user, {"super_admin"})
    events = db.scalars(
        select(AdminAuditEvent).order_by(AdminAuditEvent.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return [
        {"id": str(e.id), "admin_id": str(e.admin_id), "action": e.action,
         "target_type": e.target_type, "target_id": e.target_id,
         "detail": e.detail, "created_at": e.created_at.isoformat()}
        for e in events
    ]
