"""P2-002 core domain models

Creates the 8 core Phase 2 tables defined by DEC-0006 (§2, §4, §10):
users, songs, audio_files, separation_jobs, tags, song_tags, usage_events,
daily_usage. No deferred tables (Rating, Coupon, CouponRedemption, SignedUrlGrant,
ContentReport, AdminAuditEvent) are created here.

Constraint and index names are explicit and match the DEC-0005 naming convention so
migrations stay deterministic. No connection string or credential is embedded; the
URL comes from app.config at run time. This migration is never auto-run at app or
container startup.

Revision ID: p2_002_core_domain_models
Revises:
Create Date: 2026-07-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "p2_002_core_domain_models"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint(
            "status IN ('active', 'blocked', 'deleted')",
            name="ck_users_status_allowed",
        ),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tags"),
        sa.UniqueConstraint("slug", name="uq_tags_slug"),
    )

    op.create_table(
        "songs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_songs"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_songs_user_id_users"
        ),
        sa.CheckConstraint(
            "status IN ('uploaded', 'processing', 'ready', 'failed')",
            name="ck_songs_status_allowed",
        ),
    )
    op.create_index("ix_songs_user_id", "songs", ["user_id", "created_at"])
    op.create_index("ix_songs_status", "songs", ["status"])

    op.create_table(
        "audio_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("song_id", sa.Uuid(), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("duration_seconds", sa.Numeric(), nullable=True),
        sa.Column("original_filename", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audio_files"),
        sa.ForeignKeyConstraint(
            ["song_id"], ["songs.id"], name="fk_audio_files_song_id_songs"
        ),
        sa.UniqueConstraint(
            "storage_key", name="uq_audio_files_storage_key"
        ),
        sa.UniqueConstraint(
            "song_id", "purpose", name="uq_audio_files_song_id"
        ),
        sa.CheckConstraint(
            "purpose IN ('original', 'vocals', 'background')",
            name="ck_audio_files_purpose_allowed",
        ),
    )
    op.create_index("ix_audio_files_song_id", "audio_files", ["song_id"])

    op.create_table(
        "separation_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("song_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("model_tier", sa.String(length=32), nullable=True),
        sa.Column("error_message", sa.String(length=1024), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_separation_jobs"),
        sa.ForeignKeyConstraint(
            ["song_id"], ["songs.id"], name="fk_separation_jobs_song_id_songs"
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed', 'canceled')",
            name="ck_separation_jobs_status_allowed",
        ),
        sa.CheckConstraint(
            "model_tier IN ('basic')", name="ck_separation_jobs_model_tier_allowed"
        ),
    )
    op.create_index(
        "ix_separation_jobs_song_id", "separation_jobs", ["song_id", "created_at"]
    )
    op.create_index("ix_separation_jobs_status", "separation_jobs", ["status"])

    op.create_table(
        "song_tags",
        sa.Column("song_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("song_id", "tag_id", name="pk_song_tags"),
        sa.ForeignKeyConstraint(
            ["song_id"], ["songs.id"], name="fk_song_tags_song_id_songs"
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["tags.id"], name="fk_song_tags_tag_id_tags"
        ),
    )
    op.create_index("ix_song_tags_tag_id", "song_tags", ["tag_id"])

    op.create_table(
        "usage_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("song_id", sa.Uuid(), nullable=False),
        sa.Column("separation_job_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_usage_events"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_usage_events_user_id_users"
        ),
        sa.ForeignKeyConstraint(
            ["song_id"], ["songs.id"], name="fk_usage_events_song_id_songs"
        ),
        sa.ForeignKeyConstraint(
            ["separation_job_id"],
            ["separation_jobs.id"],
            name="fk_usage_events_separation_job_id_separation_jobs",
        ),
        sa.UniqueConstraint(
            "song_id", "event_type", name="uq_usage_events_song_id"
        ),
        sa.CheckConstraint(
            "event_type IN ('separation_succeeded')",
            name="ck_usage_events_event_type_allowed",
        ),
    )
    op.create_index(
        "ix_usage_events_user_id", "usage_events", ["user_id", "created_at"]
    )

    op.create_table(
        "daily_usage",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column(
            "successful_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_daily_usage"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_daily_usage_user_id_users"
        ),
        sa.UniqueConstraint(
            "user_id", "usage_date", name="uq_daily_usage_user_id"
        ),
    )
    op.create_index("ix_daily_usage_usage_date", "daily_usage", ["usage_date"])


def downgrade() -> None:
    op.drop_index("ix_daily_usage_usage_date", table_name="daily_usage")
    op.drop_table("daily_usage")

    op.drop_index("ix_usage_events_user_id", table_name="usage_events")
    op.drop_table("usage_events")

    op.drop_index("ix_song_tags_tag_id", table_name="song_tags")
    op.drop_table("song_tags")

    op.drop_index("ix_separation_jobs_status", table_name="separation_jobs")
    op.drop_index("ix_separation_jobs_song_id", table_name="separation_jobs")
    op.drop_table("separation_jobs")

    op.drop_index("ix_audio_files_song_id", table_name="audio_files")
    op.drop_table("audio_files")

    op.drop_index("ix_songs_status", table_name="songs")
    op.drop_index("ix_songs_user_id", table_name="songs")
    op.drop_table("songs")

    op.drop_table("tags")
    op.drop_table("users")
