"""Auth package — local MVP authentication (Phase 3).

Re-exports the public API so that existing imports like
``from app.auth import current_user, get_db`` continue to work unchanged.
"""

from .password import (
    hash_password,
    verify_password,
    _DUMMY_PASSWORD_HASH,
)
from .schemas import (
    AuthMessage,
    AuthUserRead,
    GoogleLoginRequest,
    LoginRequest,
    SignupRequest,
)
from .session import (
    ACTIVE_STATUS,
    SESSION_COOKIE_NAME,
    SESSION_TTL,
    clear_auth_cookie,
    create_session_token,
    current_user,
    get_db,
    hash_session_token,
    set_auth_cookie,
)
from .routes import (
    MAX_EMAIL_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    router,
)

__all__ = [
    # Router
    "router",
    # Guard + DB dependency
    "current_user",
    "get_db",
    # Password
    "hash_password",
    "verify_password",
    "_DUMMY_PASSWORD_HASH",
    # Session / cookie
    "ACTIVE_STATUS",
    "SESSION_COOKIE_NAME",
    "SESSION_TTL",
    "clear_auth_cookie",
    "create_session_token",
    "hash_session_token",
    "set_auth_cookie",
    # Validation constants
    "MIN_PASSWORD_LENGTH",
    "MAX_PASSWORD_LENGTH",
    "MAX_EMAIL_LENGTH",
    # Schemas
    "AuthMessage",
    "AuthUserRead",
    "GoogleLoginRequest",
    "LoginRequest",
    "SignupRequest",
]
