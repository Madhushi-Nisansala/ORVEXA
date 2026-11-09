"""Add safe document lifecycle metadata.

Revision ID: 0004_document_lifecycle
Revises: 0003_stage1b_domain_foundation
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_document_lifecycle"
down_revision: Union[str, Sequence[str], None] = "0003_stage1b_domain_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column("documents", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
	op.add_column("documents", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
	op.create_index("ix_documents_user_archived_at", "documents", ["user_id", "archived_at"])


def downgrade() -> None:
	op.drop_index("ix_documents_user_archived_at", table_name="documents")
	op.drop_column("documents", "deleted_at")
	op.drop_column("documents", "archived_at")
