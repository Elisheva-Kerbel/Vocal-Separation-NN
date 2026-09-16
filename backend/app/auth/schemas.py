"""Request / response models for auth (DEC-0010 D9).

Defined here, not in ``app/schemas``, to keep the class set closed per DEC-0007.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import UserRole, UserTier


def _text_only(value: object) -> str:
    """Coerce a non-string credential field to ``""`` before validation.

    Length and shape are checked inside the routes, not by the model, so that a
    rejection is a fixed safe message.  This is the other half of that rule: a
    framework validation error echoes the offending input back in its body, and no
    submitted credential may be echoed anywhere — so a non-string never reaches
    validation, and the route's own safe error handles it.
    """
    return value if isinstance(value, str) else ""


class SignupRequest(BaseModel):
    """Sign-up input.  ``extra="forbid"`` closes the field set.

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
    """Sign-in input.  Same closed field set and same no-echo handling."""

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
    role: str = UserRole.FREE
    tier: str = UserTier.FREE


class AuthMessage(BaseModel):
    """A fixed, safe sentence.  Never carries detail, input or state."""

    model_config = ConfigDict(extra="forbid")

    message: str


class GoogleLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    credential: str = ""
