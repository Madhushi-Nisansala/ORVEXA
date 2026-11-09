"""Add explicit titles and category indexing for project memory."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0010_project_memory"
down_revision: Union[str, Sequence[str], None] = "0009_document_insights"
branch_labels = None
depends_on = None


def upgrade() -> None:
	with op.batch_alter_table("user_context") as batch_op:
		batch_op.add_column(sa.Column("title", sa.String(200), nullable=False, server_default="Untitled memory"))
		batch_op.create_index("ix_user_context_user_category", ["user_id", "category"])


def downgrade() -> None:
	with op.batch_alter_table("user_context") as batch_op:
		batch_op.drop_index("ix_user_context_user_category")
		batch_op.drop_column("title")