"""Session management — cookie handling, token lifecycle, ``current_user``
dependency, and the ``get_db`` helper (DEC-0010 D2, D4, D5).
"""

from __future__ import annotations

import datetime
import hashlib
import secrets
from typing import Iterator

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.config import load_settings
from app.constants import UserStatus, UserTier
from app.db.models import User, UserSession
from app.db.session import get_sessionmaker

# ---- Constants ---------------------------------------------------------------

SESSION_COOKIE_NAME = "stemspace_session"
SESSION_TTL = datetime.timedelta(days=7)

ACTIVE_STATUS = UserStatus.ACTIVE


# ---- DB dependency -----------------------------------------------------------


def get_db() -> Iterator[DbSession]:
    """Yield one request-scoped SQLAlchemy session.

    The engine is still created lazily (P2-001), so importing this module opens no
    connection.  Tests override this dependency with an in-memory database.
    """
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()


# ---- Session tokens (D2) ----------------------------------------------------


def create_session_token() -> str:
    """Mint one opaque 256-bit session token.  Returned to the caller once, to be
    put in a cookie — never persisted and never placed in a response body."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Return the SHA-256 hex of a session token — the only form ever stored.

    A fast hash is correct here (unlike for passwords): the token is 256 bits of
    system randomness, so there is nothing to brute-force.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ---- Cookie handling (D4) ----------------------------------------------------


def _cookie_secure() -> bool:
    """Send the cookie over HTTPS only, except in local development.

    Local dev runs on plain HTTP, so ``APP_ENV=local`` relaxes the flag.
    **Production requires ``Secure`` over HTTPS** — which is exactly what every
    other value of ``APP_ENV`` yields.
    """
    return load_settings().app_env != "local"


def set_auth_cookie(response: Response, token: str) -> None:
    """Attach the session cookie: httpOnly, SameSite=Lax, path=/ (D4)."""
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=_cookie_secure(),
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """Remove the session cookie, with the flags it was set with."""
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
        secure=_cookie_secure(),
    )


# ---- Internal helpers --------------------------------------------------------


def _error(status_code: int, code: str, message: str) -> HTTPException:
    """Build a safe error: a fixed code plus fixed text, and nothing else."""
    return HTTPException(
        status_code=status_code, detail={"error": code, "message": message}
    )


def _not_authenticated() -> HTTPException:
    return _error(401, "not_authenticated", "Sign in to continue.")


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _as_utc(value: datetime.datetime) -> datetime.datetime:
    """Read a stored timestamp as UTC-aware.

    PostgreSQL round-trips ``timestamptz`` as tz-aware.  SQLite (used by the DB
    tests) has no timestamp type and hands back a naive value, which cannot be
    compared with an aware one — it is UTC by construction, so it is labelled here.
    """
    return value if value.tzinfo else value.replace(tzinfo=datetime.timezone.utc)


def _lookup_session(db: DbSession, token: str) -> UserSession | None:
    """Resolve a raw token to a live session row, or ``None``.

    The lookup is by token *hash*, so the raw token is never compared against
    stored data.  An expired row is deleted on the spot (D5) — that is the whole
    of session cleanup; there is no background sweeper.
    """
    session = db.scalars(
        select(UserSession).where(UserSession.token_hash == hash_session_token(token))
    ).first()
    if session is None:
        return None
    if _as_utc(session.expires_at) <= _now():
        db.delete(session)
        db.commit()
        return None
    return session


def _start_session(db: DbSession, user: User, response: Response) -> None:
    """Mint a session for ``user``, store only its hash, and set the cookie."""
    token = create_session_token()
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            expires_at=_now() + SESSION_TTL,
        )
    )
    db.commit()
    set_auth_cookie(response, token)


# ---- Permission guard --------------------------------------------------------


def current_user(
    request: Request, db: DbSession = Depends(get_db)
) -> User:
    """The permission guard every future protected route depends on.

    ``401`` when the cookie is missing, unknown or expired; ``403`` when the
    account is not ``active``, which is what makes DEC-0010 D1's "a blocked user
    cannot act" enforceable — a blocked or deleted user's **existing** session
    stops working immediately, with no token to revoke.
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise _not_authenticated()

    session = _lookup_session(db, token)
    if session is None:
        raise _not_authenticated()

    user = db.get(User, session.user_id)
    if user is None:
        raise _not_authenticated()
    if user.status == UserStatus.BLOCKED:
        raise _error(403, "account_blocked", "החשבון שלך נחסם על ידי מנהל המערכת. לבירורים, פנה/י להנהלה.")
    if user.status != ACTIVE_STATUS:
        raise _error(403, "account_not_active", "This account is not active.")

    if user.tier == UserTier.PRO and user.subscription_expires_at:
        if _as_utc(user.subscription_expires_at) <= _now():
            user.tier = UserTier.FREE
            user.subscription_expires_at = None
            db.commit()

    return user
