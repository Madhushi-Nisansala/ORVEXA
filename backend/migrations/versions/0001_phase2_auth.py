"""Create Phase 2 authentication schema.

Revision ID: 0001_phase2_auth
Revises:
Create Date: 2026-11-08
"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa

revision: str = "0001_phase2_auth"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	user_roles = sa.Table(
		"user_roles",
		sa.MetaData(),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("role_id", sa.Uuid(), nullable=False),
	)
	op.create_table(
		"users",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("email", sa.String(length=320), nullable=False),
		sa.Column("password_hash", sa.String(length=512), nullable=False),
		sa.Column("full_name", sa.String(length=200), nullable=True),
		sa.Column("preferred_language", sa.String(length=2), nullable=False),
		sa.Column("is_active", sa.Boolean(), nullable=False),
		sa.Column("is_verified", sa.Boolean(), nullable=False),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
		sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
		sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_users_email", "users", ["email"], unique=True)
	op.create_table(
		"roles",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("name", sa.String(length=50), nullable=False),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_roles_name", "roles", ["name"], unique=True)
	op.create_table(
		"user_roles",
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("role_id", sa.Uuid(), nullable=False),
		sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("user_id", "role_id"),
	)
	op.create_table(
		"refresh_tokens",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("token_hash", sa.String(length=128), nullable=False),
		sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
		sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
		sa.Column("replaced_by_token_id", sa.Uuid(), nullable=True),
		sa.Column("device_name", sa.String(length=200), nullable=True),
		sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
		sa.ForeignKeyConstraint(["replaced_by_token_id"], ["refresh_tokens.id"], ondelete="SET NULL"),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
	op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
	op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])
	role_table = sa.table(
		"roles",
		sa.column("id", sa.Uuid()),
		sa.column("name", sa.String(length=50)),
	)
	op.bulk_insert(
		role_table,
		[
			{"id": uuid.UUID("00000000-0000-0000-0000-000000000001"), "name": "user"},
			{"id": uuid.UUID("00000000-0000-0000-0000-000000000002"), "name": "admin"},
		],
	)


def downgrade() -> None:
	op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")
	op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
	op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
	op.drop_table("refresh_tokens")
	op.drop_table("user_roles")
	op.drop_index("ix_roles_name", table_name="roles")
	op.drop_table("roles")
	op.drop_index("ix_users_email", table_name="users")
	op.drop_table("users")
