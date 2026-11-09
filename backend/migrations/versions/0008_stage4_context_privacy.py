"""Add privacy-aware personal context and insight evidence links.

Revision ID: 0008_stage4_context_privacy
Revises: 0007_stage3_document_analysis
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008_stage4_context_privacy"
down_revision: Union[str, Sequence[str], None] = "0007_stage3_document_analysis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
		"user_context",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("context_type", sa.String(32), nullable=False),
		sa.Column("category", sa.String(64), nullable=False),
		sa.Column("content", sa.JSON(), nullable=False),
		sa.Column("source_type", sa.String(32), nullable=False),
		sa.Column("source_reference", sa.String(500)),
		sa.Column("evidence_reference", sa.Uuid()),
		sa.Column("confidence", sa.String(16)),
		sa.Column("confirmation_status", sa.String(16), nullable=False, server_default="unconfirmed"),
		sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
		sa.Column("review_after", sa.DateTime(timezone=True)),
		sa.Column("expires_at", sa.DateTime(timezone=True)),
		sa.Column("retention_policy", sa.String(32), nullable=False, server_default="user_controlled"),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.Column("deleted_at", sa.DateTime(timezone=True)),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["evidence_reference"], ["evidence_sources.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_user_context_user_active", "user_context", ["user_id", "is_active"])
	op.create_index("ix_user_context_review_after", "user_context", ["review_after"])

	op.create_table(
		"context_preferences",
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("persistent_memory_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("allow_document_derived_context", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("allow_interaction_derived_context", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("default_retention_days", sa.Integer()),
		sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("user_id"),
	)

	op.create_table(
		"insight_evidence",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("insight_id", sa.Uuid(), nullable=False),
		sa.Column("evidence_source_id", sa.Uuid(), nullable=False),
		sa.Column("relation", sa.String(32), nullable=False, server_default="supports"),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["insight_id"], ["intelligence_insights.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["evidence_source_id"], ["evidence_sources.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
		sa.UniqueConstraint("insight_id", "evidence_source_id", name="uq_insight_evidence_link"),
	)
	op.create_index("ix_insight_evidence_user_id", "insight_evidence", ["user_id"])


def downgrade() -> None:
	raise NotImplementedError("ORVEXA migrations are forward-only")
