"""Centralized domain constants -- single source of truth for every
status / role / tier / purpose value used in queries and route logic."""

from enum import StrEnum


class SongStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class UserStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"


class Visibility(StrEnum):
    PRIVATE = "private"
    PUBLIC = "public"


class UserRole(StrEnum):
    FREE = "free"
    PRO = "pro"
    CONTENT_MODERATOR = "content_moderator"
    USER_ADMIN = "user_admin"
    COUPON_ADMIN = "coupon_admin"
    SUPER_ADMIN = "super_admin"


ADMIN_ROLES = frozenset({
    UserRole.CONTENT_MODERATOR,
    UserRole.USER_ADMIN,
    UserRole.COUPON_ADMIN,
    UserRole.SUPER_ADMIN,
})


class UserTier(StrEnum):
    FREE = "free"
    PRO = "pro"


class AudioPurpose(StrEnum):
    ORIGINAL = "original"
    VOCALS = "vocals"
    BACKGROUND = "background"


VALID_PURPOSES = frozenset(AudioPurpose)


class ModelTier(StrEnum):
    BASIC = "basic"
    PROFESSIONAL = "professional"


class ReportStatus(StrEnum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"
    DISMISSED = "dismissed"


class GrantType(StrEnum):
    LISTEN = "listen"
    DOWNLOAD = "download"


GOOGLE_OAUTH_SENTINEL = "google_oauth"
STEM_OUTPUT_CONTENT_TYPE = "audio/wav"
MAX_TITLE_LENGTH = 256
