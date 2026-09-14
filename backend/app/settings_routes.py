"""Settings + Account Deletion routes (Phase 11)."""

from __future__ import annotations

import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.auth import clear_auth_cookie, current_user, get_db, hash_password, verify_password, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH
from app.db.models import AudioFile, Song, User, UserSession
from fastapi import Response

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preferred_language: str | None = None
    email_opt_in: bool | None = None


class SettingsView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str
    preferred_language: str | None
    email_opt_in: bool
    tier: str
    role: str


class DeleteAccountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirm: bool


@router.get("", response_model=SettingsView)
def get_settings(user: User = Depends(current_user)) -> SettingsView:
    return SettingsView(
        email=user.email,
        preferred_language=user.preferred_language,
        email_opt_in=user.email_opt_in,
        tier=user.tier,
        role=user.role,
    )


@router.patch("", response_model=SettingsView)
def update_settings(
    payload: SettingsUpdate,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> SettingsView:
    if payload.preferred_language is not None:
        user.preferred_language = payload.preferred_language
    if payload.email_opt_in is not None:
        user.email_opt_in = payload.email_opt_in
    db.commit()
    db.refresh(user)
    return SettingsView(
        email=user.email,
        preferred_language=user.preferred_language,
        email_opt_in=user.email_opt_in,
        tier=user.tier,
        role=user.role,
    )


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str = ""
    new_password: str = ""


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    if user.password_hash == "google_oauth":
        raise HTTPException(status_code=400, detail={"error": "google_account", "message": "חשבון Google — אין אפשרות לשנות סיסמה."})
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail={"error": "wrong_password", "message": "הסיסמה הנוכחית שגויה."})
    if not MIN_PASSWORD_LENGTH <= len(payload.new_password) <= MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_password", "message": f"הסיסמה חייבת להיות {MIN_PASSWORD_LENGTH}–{MAX_PASSWORD_LENGTH} תווים."},
        )
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "הסיסמה שונתה בהצלחה."}


@router.post("/toggle-tier")
def toggle_tier(
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail={"error": "forbidden", "message": "Admin only."})
    if user.tier == "pro":
        raise HTTPException(status_code=400, detail={"error": "cannot_downgrade", "message": "לא ניתן לרדת מרמה מקצועית."})
    user.tier = "pro"
    db.commit()
    return {"tier": user.tier, "message": f"Tier switched to {user.tier}."}


@router.post("/delete-account")
def delete_account(
    payload: DeleteAccountRequest,
    response: Response,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
) -> dict:
    if not payload.confirm:
        raise HTTPException(status_code=400, detail={"error": "confirmation_required", "message": "You must confirm account deletion."})

    songs = db.scalars(select(Song).where(Song.user_id == user.id)).all()
    for song in songs:
        song.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        song.visibility = "private"

    sessions = db.scalars(select(UserSession).where(UserSession.user_id == user.id)).all()
    for session in sessions:
        db.delete(session)

    user.status = "deleted"
    user.email = f"deleted_{user.id}@deleted.local"

    db.commit()
    clear_auth_cookie(response)
    return {"message": "Account deleted. Your data will be removed."}
