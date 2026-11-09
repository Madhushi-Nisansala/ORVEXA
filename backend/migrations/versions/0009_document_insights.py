"""Persist insights generated from document analyses."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009_document_insights"
down_revision: Union[str, Sequence[str], None] = "0008_stage4_context_privacy"
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		"document_insights",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("document_id", sa.Uuid(), nullable=False),
		sa.Column("analysis_id", sa.Uuid(), nullable=False),
		sa.Column("title", sa.String(200), nullable=False),
		sa.Column("description", sa.Text(), nullable=False),
		sa.Column("category", sa.String(32), nullable=False),
		sa.Column("importance", sa.Integer()),
		sa.Column("confidence", sa.Float()),
		sa.Column("status", sa.String(32), nullable=False, server_default="active"),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
	sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
	sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
	sa.ForeignKeyConstraint(["analysis_id"], ["document_analyses.id"], ondelete="CASCADE"),
	sa.PrimaryKeyConstraint("id"),
	sa.UniqueConstraint("analysis_id", "title", name="uq_document_insights_analysis_title"),
	)
	op.create_index("ix_document_insights_user_id", "document_insights", ["user_id"])
	op.create_index("ix_document_insights_document_id", "document_insights", ["document_id"])


def downgrade() -> None:
	op.drop_index("ix_document_insights_document_id", table_name="document_insights")
	op.drop_index("ix_document_insights_user_id", table_name="document_insights")
	op.drop_table("document_insights")