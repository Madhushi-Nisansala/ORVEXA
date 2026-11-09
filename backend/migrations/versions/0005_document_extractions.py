"""Add document extraction metadata.

Revision ID: 0005_document_extractions
Revises: 0004_document_lifecycle
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_document_extractions"
down_revision: Union[str, Sequence[str], None] = "0004_document_lifecycle"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
		"document_extractions",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("document_id", sa.Uuid(), nullable=False),
		sa.Column("extractor_type", sa.String(64), nullable=False),
		sa.Column("extractor_version", sa.String(32), nullable=False),
		sa.Column("detected_language", sa.String(16)),
		sa.Column("status", sa.String(32), nullable=False, server_default="processing"),
		sa.Column("error_code", sa.String(64)),
		sa.Column("error_summary", sa.String(500)),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.Column("completed_at", sa.DateTime(timezone=True)),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_document_extractions_user_id", "document_extractions", ["user_id"])
	op.create_index("ix_document_extractions_document_id", "document_extractions", ["document_id"])


def downgrade() -> None:
	op.drop_index("ix_document_extractions_document_id", table_name="document_extractions")
	op.drop_index("ix_document_extractions_user_id", table_name="document_extractions")
	op.drop_table("document_extractions")
