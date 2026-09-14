"""Split daily_usage into basic_count and professional_count.

Revision ID: p12_quota_split
Revises: p4_p11_full
Create Date: 2026-08-24
"""

from alembic import op
import sqlalchemy as sa

revision = "p12_quota_split"
down_revision = "p4_p11_full"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("daily_usage", sa.Column("basic_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("daily_usage", sa.Column("professional_count", sa.Integer(), nullable=False, server_default="0"))
    op.execute("UPDATE daily_usage SET basic_count = successful_count")


def downgrade() -> None:
    op.drop_column("daily_usage", "professional_count")
    op.drop_column("daily_usage", "basic_count")
