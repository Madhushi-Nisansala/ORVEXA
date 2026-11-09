"""Add indexes supporting ownership-scoped global search."""

from typing import Sequence, Union

from alembic import op


revision: str = "0011_global_search_indexes"
down_revision: Union[str, Sequence[str], None] = "0010_project_memory"
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_index("ix_documents_search_scope", "documents", ["user_id", "deleted_at", "archived_at", "created_at"])
	op.create_index("ix_tasks_search_scope", "tasks", ["user_id", "status", "created_at"])
	op.create_index("ix_goals_search_scope", "goals", ["user_id", "status", "created_at"])
	op.create_index("ix_intelligence_insights_search_scope", "intelligence_insights", ["user_id", "category", "status", "created_at"])
	op.create_index("ix_user_context_search_scope", "user_context", ["user_id", "is_active", "category", "created_at"])


def downgrade() -> None:
	op.drop_index("ix_user_context_search_scope", table_name="user_context")
	op.drop_index("ix_intelligence_insights_search_scope", table_name="intelligence_insights")
	op.drop_index("ix_goals_search_scope", table_name="goals")
	op.drop_index("ix_tasks_search_scope", table_name="tasks")
	op.drop_index("ix_documents_search_scope", table_name="documents")
