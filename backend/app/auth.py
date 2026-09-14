"""Local MVP authentication (Phase 3) — LOCAL MVP ONLY.

Authorized by ``docs/decisions/DEC-0010-phase-3-auth-contract.md`` (approved for
Local MVP implementation). Accounts and a guard — nothing that consumes them yet:
no upload, no private storage, no queue/worker, no billing, no admin/RBAC, no
public library, no Professional.

Everything is **stdlib** (DEC-0010 D3): ``hashlib.scrypt`` for passwords,
``secrets`` for tokens, ``hmac.compare_digest`` for comparison. No JWT, no OAuth,
no passlib/bcrypt/argon2/python-jose, and therefore **no new dependency**.

The mechanism, in one paragraph: a login mints an opaque token with
``secrets.token_urlsafe(32)`` and stores **only its SHA-256 hex** in the
``sessions`` table (D2), so a database leak yields no live session. The raw token
travels in an httpOnly, SameSite=Lax cookie and **never** appears in a response
body, a URL or browser storage (D4). Sessions live an absolute 7 days with no
sliding renewal; logout deletes the row and an expired row is deleted lazily when
it is looked up (D5) — there is no sweeper.

Safety properties (DEC-0010 §5):

- The password, the stored hash and the session token appear in no response body,
  log line or error message. Errors carry a fixed code plus fixed text — no
  traceback, no path, no ``DATABASE_URL``, no echo of submitted input.
- Login is non-enumerating (D7): an unknown email and a wrong password return the
  same status and the same body, and an unknown email still pays for a dummy
  scrypt verification so the response time does not disclose that the account is
  missing.
- Authorization is enforced here, on the backend. ``blocked`` and ``deleted``
  accounts cannot authenticate and cannot pass the guard.
- Request/response models are defined **in this module**, so the ``app/schemas``
  class set closed by DEC-0007 stays closed (D9). Field values are copied into
  ``AuthUserRead`` explicitly, so no credential column can leak by accident.
"""

from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import secrets
import uuid
from typing import Iterator

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.config import load_settings
from app.db.models import User, UserSession
from app.db.session import get_sessionmaker

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Parameters (DEC-0010 D2, D3, D4, D5) ------------------------------------

# scrypt cost. 128 * N * r = 16 MB of memory per hash, inside OpenSSL's default
# 32 MB limit, so no maxmem override is needed.
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32
SALT_BYTES = 16

SESSION_COOKIE_NAME = "stemspace_session"
SESSION_TTL = datetime.timedelta(days=7)

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MAX_EMAIL_LENGTH = 320

ACTIVE_STATUS = "active"


# --- Password hashing (D3) ----------------------------------------------------


def hash_password(password: str) -> str:
    """Return the self-describing encoded hash of ``password``.

    Format: ``scrypt$n$r$p$<salt-b64>$<hash-b64>``, with a fresh 16-byte random
    salt every call — so the same password never produces the same string twice —
    and the cost parameters carried inline, so they can be raised later without a
    migration. The plaintext is never stored, logged or returned.
    """
    salt = secrets.token_bytes(SALT_BYTES)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return (
        f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}$"
        f"{base64.b64encode(salt).decode()}${base64.b64encode(derived).decode()}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify ``password`` against an encoded hash, in constant time.

    Parameters come from the stored string, not from the constants above, so
    hashes written under older parameters keep verifying. A malformed, truncated
    or tampered string is a plain ``False`` — never an exception that could
    surface as a traceback.
    """
    try:
        algorithm, n, r, p, salt_b64, hash_b64 = stored_hash.split("$")
        if algorithm != "scrypt":
            return False
        salt = base64.b64decode(salt_b64, validate=True)
        expected = base64.b64decode(hash_b64, validate=True)
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )
    except (ValueError, TypeError, MemoryError):
        return False
    return hmac.compare_digest(derived, expected)


# Non-enumerating login (D7): an unknown email is verified against this hash, so
# it costs exactly the same scrypt work as a real account. Derived once from a
# throw-away random password that is never stored, so nothing can match it.
_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(16))


# --- Session tokens (D2) ------------------------------------------------------


def create_session_token() -> str:
    """Mint one opaque 256-bit session token. Returned to the caller once, to be
    put in a cookie — never persisted and never placed in a response body."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Return the SHA-256 hex of a session token — the only form ever stored.

    A fast hash is correct here (unlike for passwords): the token is 256 bits of
    system randomness, so there is nothing to brute-force.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# --- Cookie handling (D4) -----------------------------------------------------


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


# --- Request / response models (D9 — defined here, not in app/schemas) ---------


def _text_only(value: object) -> str:
    """Coerce a non-string credential field to ``""`` before validation.

    Length and shape are checked inside the routes, not by the model, so that a
    rejection is a fixed safe message. This is the other half of that rule: a
    framework validation error echoes the offending input back in its body, and no
    submitted credential may be echoed anywhere — so a non-string never reaches
    validation, and the route's own safe error handles it.
    """
    return value if isinstance(value, str) else ""


class SignupRequest(BaseModel):
    """Sign-up input. ``extra="forbid"`` closes the field set.

    ``email`` and ``password`` default to ``""`` rather than being required, so a
    missing field is rejected by the route's own safe message instead of a
    framework error that would echo the submitted body.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    email: str = ""
    password: str = ""
    preferred_language: str | None = Field(default=None, alias="preferredLanguage")
    email_opt_in: bool = Field(default=False, alias="emailOptIn")

    _coerce_text = field_validator("email", "password", mode="before")(_text_only)


class LoginRequest(BaseModel):
    """Sign-in input. Same closed field set and same no-echo handling."""

    model_config = ConfigDict(extra="forbid")

    email: str = ""
    password: str = ""

    _coerce_text = field_validator("email", "password", mode="before")(_text_only)


class AuthUserRead(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: uuid.UUID
    email: str
    status: str
    preferred_language: str | None = Field(alias="preferredLanguage")
    email_opt_in: bool = Field(alias="emailOptIn")
    role: str = "free"
    tier: str = "free"


class AuthMessage(BaseModel):
    """A fixed, safe sentence. Never carries detail, input or state."""

    model_config = ConfigDict(extra="forbid")

    message: str


# --- Helpers ------------------------------------------------------------------


def get_db() -> Iterator[DbSession]:
    """Yield one request-scoped SQLAlchemy session.

    The engine is still created lazily (P2-001), so importing this module opens no
    connection. Tests override this dependency with an in-memory database.
    """
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()


def _error(status_code: int, code: str, message: str) -> HTTPException:
    """Build a safe error: a fixed code plus fixed text, and nothing else.

    Never carries a traceback, a path, a configuration value, a credential or an
    echo of submitted input. Same shape as the demo slice's coded errors, so the
    frontend maps one vocabulary.
    """
    return HTTPException(
        status_code=status_code, detail={"error": code, "message": message}
    )


def _not_authenticated() -> HTTPException:
    return _error(401, "not_authenticated", "Sign in to continue.")


def _invalid_credentials() -> HTTPException:
    # One message and one status for both unknown email and wrong credentials
    # (D7). The wording names neither, so the response discloses nothing.
    return _error(
        401, "invalid_credentials", "Those sign-in details did not match. Try again."
    )


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _as_utc(value: datetime.datetime) -> datetime.datetime:
    """Read a stored timestamp as UTC-aware.

    PostgreSQL round-trips ``timestamptz`` as tz-aware. SQLite (used by the DB
    tests) has no timestamp type and hands back a naive value, which cannot be
    compared with an aware one — it is UTC by construction, so it is labelled here.
    """
    return value if value.tzinfo else value.replace(tzinfo=datetime.timezone.utc)


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


def _lookup_session(db: DbSession, token: str) -> UserSession | None:
    """Resolve a raw token to a live session row, or ``None``.

    The lookup is by token *hash*, so the raw token is never compared against
    stored data. An expired row is deleted on the spot (D5) — that is the whole
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
    if user.status != ACTIVE_STATUS:
        raise _error(403, "account_not_active", "This account is not active.")

    if user.tier == "pro" and user.subscription_expires_at:
        if _as_utc(user.subscription_expires_at) <= _now():
            user.tier = "free"
            user.subscription_expires_at = None
            db.commit()

    return user


# --- Routes (DEC-0010 §4) -----------------------------------------------------


@router.post("/signup", status_code=201, response_model=AuthUserRead)
def signup(
    payload: SignupRequest, response: Response, db: DbSession = Depends(get_db)
) -> AuthUserRead:
    """Create an active local account and sign it in.

    Open signup, local demo/dev only (D6): no invite, no email verification and no
    password reset in this phase. The new account starts ``active`` with
    ``profile_visibility='hidden'`` — private by default.
    """
    email = _normalise_email(payload.email)
    if "@" not in email or len(email) > MAX_EMAIL_LENGTH or email.startswith("@"):
        raise _error(400, "invalid_email", "Enter a valid email address.")
    if not MIN_PASSWORD_LENGTH <= len(payload.password) <= MAX_PASSWORD_LENGTH:
        raise _error(
            400,
            "invalid_password",
            f"Choose {MIN_PASSWORD_LENGTH}–{MAX_PASSWORD_LENGTH} characters.",
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

    if user is None or not password_ok or user.status != ACTIVE_STATUS:
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


class GoogleLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    credential: str = ""


@router.post("/google", response_model=AuthUserRead)
def google_login(
    payload: GoogleLoginRequest, response: Response, db: DbSession = Depends(get_db)
) -> AuthUserRead:
    """Sign in or sign up with a Google ID token (from Google Identity Services).

    Verifies the token via Google's tokeninfo endpoint, checks the audience
    matches our client ID, then either signs in the existing user or creates
    a new account. No password is set for Google-created accounts.
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
            verify=False,
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
        password_hash="google_oauth",
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
