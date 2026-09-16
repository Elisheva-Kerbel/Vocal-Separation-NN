"""Models package — re-exports all ORM model classes.

Existing imports like ``from app.db.models import User, Song`` continue to work.
"""

from .mixins import CreatedAtMixin, UpdatedAtMixin
from .user import User, UserSession
from .song import AudioFile, SeparationJob, Song
from .social import ContentReport, Rating, SongTag, Tag
from .billing import Coupon, CouponRedemption, DailyUsage, UsageEvent
from .admin import AdminAuditEvent, SignedUrlGrant

__all__ = [
    # Mixins
    "CreatedAtMixin",
    "UpdatedAtMixin",
    # User
    "User",
    "UserSession",
    # Song
    "AudioFile",
    "SeparationJob",
    "Song",
    # Social
    "ContentReport",
    "Rating",
    "SongTag",
    "Tag",
    # Billing
    "Coupon",
    "CouponRedemption",
    "DailyUsage",
    "UsageEvent",
    # Admin
    "AdminAuditEvent",
    "SignedUrlGrant",
]
