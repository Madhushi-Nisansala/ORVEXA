"""Add versioned document intelligence analysis artifacts.

Revision ID: 0007_stage3_document_analysis
Revises: 0006_stage2_extraction_jobs
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_stage3_document_analysis"
down_revision: Union[str, Sequence[str], None] = "0006_stage2_extraction_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
		"document_analyses",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("document_id", sa.Uuid(), nullable=False),
		sa.Column("extraction_id", sa.Uuid(), nullable=False),
		sa.Column("version", sa.Integer(), nullable=False),
		sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
		sa.Column("provider_identifier", sa.String(128), nullable=True),
		sa.Column("model_name", sa.String(128), nullable=True),
		sa.Column("result", sa.JSON(), nullable=True),
		sa.Column("error_code", sa.String(64), nullable=True),
		sa.Column("error_summary", sa.String(500), nullable=True),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["extraction_id"], ["document_extractions.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
		sa.UniqueConstraint("document_id", "version", name="uq_document_analyses_document_version"),
	)
	op.create_index("ix_document_analyses_user_id", "document_analyses", ["user_id"])
	op.create_index("ix_document_analyses_document_id", "document_analyses", ["document_id"])


def downgrade() -> None:
	op.drop_index("ix_document_analyses_document_id", table_name="document_analyses")
	op.drop_index("ix_document_analyses_user_id", table_name="document_analyses")
	op.drop_table("document_analyses")
