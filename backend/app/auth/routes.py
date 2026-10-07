"""Auth route handlers (DEC-0010 section 4).

All routes are mounted on an ``APIRouter`` with prefix ``/auth``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.config import load_settings
from app.constants import GOOGLE_OAUTH_SENTINEL, UserStatus
from app.db.models import PasswordResetToken, User

from .password import (
    _DUMMY_PASSWORD_HASH,
    hash_password,
    verify_password,
)
from .schemas import (
    AuthMessage,
    AuthUserRead,
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    ResetPasswordRequest,
    SignupRequest,
)
from .session import (
    ACTIVE_STATUS,
    SESSION_COOKIE_NAME,
    _lookup_session,
    _start_session,
    clear_auth_cookie,
    current_user,
    get_db,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# ---- Validation constants ----------------------------------------------------

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MAX_EMAIL_LENGTH = 320


# ---- Internal helpers --------------------------------------------------------


def _error(status_code: int, code: str, message: str):
    from fastapi import HTTPException

    return HTTPException(
        status_code=status_code, detail={"error": code, "message": message}
    )


def _invalid_credentials():
    # One message and one status for both unknown email and wrong credentials
    # (D7).  The wording names neither, so the response discloses nothing.
    return _error(
        401, "invalid_credentials", "Those sign-in details did not match. Try again."
    )


def _normalise_email(email: str) -> str:
    return email.strip().lower()


def _safe_user(user: User) -> AuthUserRead:
    """Project a ``User`` row onto the safe public shape, field by field.

    Explicit copying (rather than reading the whole ORM object) is what
    guarantees ``password_hash`` can never be serialised into a response.
    """
    return AuthUserRead(
        id=user.id,
        email=user.email,
        status=user.status,
        preferred_language=user.preferred_language,
        email_opt_in=user.email_opt_in,
        role=user.role,
        tier=user.tier,
    )


def _find_user(db: DbSession, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


# ---- Route handlers ----------------------------------------------------------


@router.post("/signup", status_code=201, response_model=AuthUserRead)
def signup(
    payload: SignupRequest, response: Response, db: DbSession = Depends(get_db)
) -> AuthUserRead:
    """Create an active local account and sign it in.

    Open signup, local demo/dev only (D6): no invite, no email verification and no
    password reset in this phase.  The new account starts ``active`` with
    ``profile_visibility='hidden'`` — private by default.
    """
    email = _normalise_email(payload.email)
    if "@" not in email or len(email) > MAX_EMAIL_LENGTH or email.startswith("@"):
        raise _error(400, "invalid_email", "Enter a valid email address.")
    if not MIN_PASSWORD_LENGTH <= len(payload.password) <= MAX_PASSWORD_LENGTH:
        raise _error(
            400,
            "invalid_password",
            f"Choose {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters.",
        )
    if _find_user(db, email) is not None:
        raise _error(409, "email_taken", "That email is already registered.")

    user = User(
        email=email,
        status=ACTIVE_STATUS,
        password_hash=hash_password(payload.password),
        preferred_language=payload.preferred_language,
        email_opt_in=payload.email_opt_in,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _start_session(db, user, response)
    return _safe_user(user)


@router.post("/login", response_model=AuthUserRead)
def login(
    payload: LoginRequest, response: Response, db: DbSession = Depends(get_db)
) -> AuthUserRead:
    """Sign in and set the session cookie.

    Non-enumerating (D7): an unknown email still runs a dummy verification, and
    unknown email, wrong password and non-active account all end in the same
    ``401`` with the same body — so nothing here reveals whether an account
    exists or has been blocked.
    """
    user = _find_user(db, _normalise_email(payload.email))
    stored_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_ok = verify_password(payload.password, stored_hash)

    if user is None or not password_ok:
        raise _invalid_credentials()
    if user.status == UserStatus.BLOCKED:
        raise _error(403, "account_blocked", "החשבון שלך נחסם על ידי מנהל המערכת. לבירורים, פנה/י להנהלה.")
    if user.status != ACTIVE_STATUS:
        raise _invalid_credentials()

    _start_session(db, user, response)
    return _safe_user(user)


@router.post("/logout", response_model=AuthMessage)
def logout(
    request: Request, response: Response, db: DbSession = Depends(get_db)
) -> AuthMessage:
    """Delete the current session row and clear the cookie.

    Idempotent and safe to call while already signed out: a missing, unknown or
    expired cookie still clears the cookie and returns the same message, so the
    response discloses nothing about session state.
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        session = _lookup_session(db, token)
        if session is not None:
            db.delete(session)
            db.commit()
    clear_auth_cookie(response)
    return AuthMessage(message="Signed out.")


@router.post("/google", response_model=AuthUserRead)
def google_login(
    payload: GoogleLoginRequest, response: Response, db: DbSession = Depends(get_db)
) -> AuthUserRead:
    """Sign in or sign up with a Google ID token (from Google Identity Services).

    Verifies the token via Google's tokeninfo endpoint, checks the audience
    matches our client ID, then either signs in the existing user or creates
    a new account.  No password is set for Google-created accounts.
    """
    import httpx

    settings = load_settings()
    if not settings.google_client_id:
        raise _error(501, "google_not_configured", "Google login is not configured.")

    if not payload.credential:
        raise _error(400, "missing_credential", "Google credential is required.")

    try:
        r = httpx.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": payload.credential},
            timeout=10,
        )
    except httpx.HTTPError:
        raise _error(502, "google_verification_failed", "Could not verify Google token.")

    if r.status_code != 200:
        raise _error(401, "invalid_google_token", "Invalid Google token.")

    token_data = r.json()

    if token_data.get("aud") != settings.google_client_id:
        raise _error(401, "invalid_google_token", "Google token audience mismatch.")

    google_email = _normalise_email(token_data.get("email", ""))
    if not google_email or not token_data.get("email_verified", False):
        raise _error(400, "unverified_email", "Google account email is not verified.")

    user = _find_user(db, google_email)

    if user is not None:
        if user.status != ACTIVE_STATUS:
            raise _error(403, "account_not_active", "This account is not active.")
        _start_session(db, user, response)
        return _safe_user(user)

    user = User(
        email=google_email,
        status=ACTIVE_STATUS,
        password_hash=GOOGLE_OAUTH_SENTINEL,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _start_session(db, user, response)
    return _safe_user(user)


@router.get("/me", response_model=AuthUserRead)
def me(user: User = Depends(current_user)) -> AuthUserRead:
    """Return the signed-in account, or ``401`` / ``403`` from the guard."""
    return _safe_user(user)


# ---- Password reset -----------------------------------------------------------

RESET_TOKEN_TTL_MINUTES = 30


@router.post("/forgot-password", response_model=AuthMessage)
def forgot_password(
    payload: ForgotPasswordRequest, db: DbSession = Depends(get_db)
) -> AuthMessage:
    """Send a password-reset email if the account exists.

    Always returns the same message regardless of whether the email is registered,
    so no account enumeration is possible.
    """
    import hashlib
    import secrets
    import datetime

    from app.email_service import send_email

    safe_msg = AuthMessage(message="If this email is registered, a reset link has been sent.")
    email = _normalise_email(payload.email)
    if "@" not in email:
        return safe_msg

    user = _find_user(db, email)
    if user is None or user.status != ACTIVE_STATUS:
        return safe_msg
    if user.password_hash == GOOGLE_OAUTH_SENTINEL:
        return safe_msg

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=RESET_TOKEN_TTL_MINUTES)

    from sqlalchemy import select, update

    db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used.is_(False))
        .values(used=True)
    )

    reset_row = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset_row)
    db.commit()

    reset_link = f"http://localhost:5173/#/reset-password?token={token}"
    html = f"""
    <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
        <h2 style="color: #7c3aed;">איפוס סיסמה - VocalSplit</h2>
        <p>שלום,</p>
        <p>קיבלנו בקשה לאיפוס הסיסמה שלך.</p>
        <p>לחצ/י על הכפתור כדי לבחור סיסמה חדשה:</p>
        <div style="text-align: center; margin: 2rem 0;">
            <a href="{reset_link}"
               style="background: #7c3aed; color: white; padding: 12px 32px;
                      border-radius: 8px; text-decoration: none; font-weight: 600;
                      display: inline-block;">
                איפוס סיסמה
            </a>
        </div>
        <p style="font-size: 0.875rem; color: #6b7280;">
            הקישור תקף ל-{RESET_TOKEN_TTL_MINUTES} דקות. אם לא ביקשת איפוס, התעלמ/י מהמייל הזה.
        </p>
        <hr style="border: none; border-top: 1px solid #e5e7eb;">
        <p style="font-size: 12px; color: #6b7280;">VocalSplit · פלטפורמת הפרדת שירים</p>
    </div>
    """
    send_email(user.email, "איפוס סיסמה - VocalSplit", html)
    return safe_msg


@router.post("/reset-password", response_model=AuthMessage)
def reset_password(
    payload: ResetPasswordRequest, db: DbSession = Depends(get_db)
) -> AuthMessage:
    """Reset a password using a valid token."""
    import hashlib
    import datetime

    from sqlalchemy import select

    if not payload.token or not payload.password:
        raise _error(400, "missing_fields", "Token and password are required.")

    if not MIN_PASSWORD_LENGTH <= len(payload.password) <= MAX_PASSWORD_LENGTH:
        raise _error(
            400, "invalid_password",
            f"Choose {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters.",
        )

    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    reset_row = db.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used.is_(False),
        )
    ).first()

    if reset_row is None:
        raise _error(400, "invalid_token", "This reset link is invalid or has already been used.")

    now = datetime.datetime.now(datetime.timezone.utc)
    if reset_row.expires_at.tzinfo is None:
        expires = reset_row.expires_at.replace(tzinfo=datetime.timezone.utc)
    else:
        expires = reset_row.expires_at

    if now > expires:
        raise _error(400, "token_expired", "This reset link has expired. Request a new one.")

    user = db.get(User, reset_row.user_id)
    if user is None or user.status != ACTIVE_STATUS:
        raise _error(400, "invalid_token", "This reset link is invalid.")

    user.password_hash = hash_password(payload.password)
    reset_row.used = True
    db.commit()

    return AuthMessage(message="Password has been reset successfully.")
