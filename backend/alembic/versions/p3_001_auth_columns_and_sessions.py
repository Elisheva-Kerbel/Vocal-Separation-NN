"""P3-001 user auth columns and sessions table

The single Phase 3 migration (DEC-0010 §3, authorized for Local MVP):

- ``users`` gains ``password_hash``, ``profile_visibility``, ``preferred_language``
  and ``email_opt_in``. ``status`` (active / blocked / deleted) already exists and
  is reused unchanged.
- New ``sessions`` table holding one opaque server-side session per login. It
  stores only the **SHA-256 hex** of the session token — never the raw token — and
  no plaintext password is stored anywhere.

No deferred entity is created here (DEC-0006 §2/§12), no seed user and no default
password. Constraint and index names are deterministic per DEC-0005: Alembic
carries the naming convention over from ``Base.metadata`` (via ``env.py``'s
``target_metadata``) and applies it to every constraint it builds, so the check
constraint is written with its convention **key** (``profile_visibility_allowed``)
on both the create and the drop and resolves to
``ck_users_profile_visibility_allowed`` on each. No connection string
or credential is embedded; the URL comes from app.config at run time. This
migration is never auto-run at app or container startup.

Revision ID: p3_001_auth_columns_and_sessions
Revises: p2_002_core_domain_models
Create Date: 2026-08-03

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "p3_001_auth_columns_and_sessions"
down_revision: Union[str, None] = "p2_002_core_domain_models"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOT NULL with no server default, exactly as DEC-0010 §3 specifies: every
    # account must have a hash, and there is deliberately no fallback value that
    # could act as a shared or empty credential.
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=False))
    op.add_column(
        "users",
        sa.Column(
            "profile_visibility",
            sa.String(length=16),
            server_default="hidden",
            nullable=False,
        ),
    )
    op.add_column("users", sa.Column("preferred_language", sa.String(length=8), nullable=True))
    op.add_column(
        "users",
        sa.Column("email_opt_in", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    # Convention key, not the final name: expands to
    # ck_users_profile_visibility_allowed via the DEC-0005 convention.
    op.create_check_constraint(
        "profile_visibility_allowed",
        "users",
        "profile_visibility IN ('hidden', 'public')",
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        # SHA-256 hex of the session token (DEC-0010 D2) — never the token itself.
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sessions"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_sessions_user_id_users"),
        sa.UniqueConstraint("token_hash", name="uq_sessions_token_hash"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")

    # Same convention key as upgrade() — Alembic expands it identically on both
    # sides, so the drop targets exactly the constraint the upgrade created.
    op.drop_constraint("profile_visibility_allowed", "users", type_="check")
    op.drop_column("users", "email_opt_in")
    op.drop_column("users", "preferred_language")
    op.drop_column("users", "profile_visibility")
    op.drop_column("users", "password_hash")
