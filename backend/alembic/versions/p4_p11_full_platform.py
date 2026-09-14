"""Phases 4-11: full platform models.

Revision ID: p4_p11_full
Revises: p3_001_auth_columns_and_sessions
Create Date: 2026-08-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "p4_p11_full"
down_revision = "p3_001_auth_columns_and_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # User: add role, tier columns
    op.add_column("users", sa.Column("role", sa.String(32), nullable=False, server_default="free"))
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=False, server_default="free"))

    # Song: add visibility, deleted_at, rights_confirmed
    op.add_column("songs", sa.Column("visibility", sa.String(16), nullable=False, server_default="private"))
    op.add_column("songs", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("songs", sa.Column("rights_confirmed", sa.Boolean(), nullable=False, server_default="false"))

    # SeparationJob: update model_tier constraint to allow 'professional'
    op.execute("ALTER TABLE separation_jobs DROP CONSTRAINT IF EXISTS \"ck_separation_jobs_ck_separation_jobs_model_tier_allowed\"")
    op.execute("ALTER TABLE separation_jobs ADD CONSTRAINT ck_separation_jobs_model_tier_allowed CHECK (model_tier IN ('basic', 'professional'))")

    # Coupons table
    op.create_table(
        "coupons",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("tier_grant", sa.String(16), nullable=False, server_default="pro"),
        sa.Column("days_valid", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("max_redemptions", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("redemption_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Coupon redemptions table
    op.create_table(
        "coupon_redemptions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("coupon_id", sa.Uuid(), sa.ForeignKey("coupons.id"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("coupon_id", "user_id"),
    )

    # Ratings table
    op.create_table(
        "ratings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("song_id", sa.Uuid(), sa.ForeignKey("songs.id"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("song_id", "user_id"),
        sa.CheckConstraint("score >= 1 AND score <= 5", name="score_range"),
    )

    # Content reports table
    op.create_table(
        "content_reports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("song_id", sa.Uuid(), sa.ForeignKey("songs.id"), nullable=False),
        sa.Column("reporter_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.String(256), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("resolved_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('pending', 'reviewed', 'actioned', 'dismissed')", name="report_status_allowed"),
    )

    # Signed URL grants table
    op.create_table(
        "signed_url_grants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("audio_file_id", sa.Uuid(), sa.ForeignKey("audio_files.id"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("grant_type", sa.String(16), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("grant_type IN ('listen', 'download')", name="grant_type_allowed"),
    )

    # Admin audit events table
    op.create_table(
        "admin_audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("admin_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_type", sa.String(32), nullable=False),
        sa.Column("target_id", sa.String(64), nullable=False),
        sa.Column("detail", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("admin_audit_events")
    op.drop_table("signed_url_grants")
    op.drop_table("content_reports")
    op.drop_table("ratings")
    op.drop_table("coupon_redemptions")
    op.drop_table("coupons")

    op.drop_column("songs", "rights_confirmed")
    op.drop_column("songs", "deleted_at")
    op.drop_column("songs", "visibility")
    op.drop_column("users", "tier")
    op.drop_column("users", "role")

    op.drop_constraint("model_tier_allowed", "separation_jobs", type_="check")
    op.create_check_constraint("model_tier_allowed", "separation_jobs", "model_tier IN ('basic')")
