"""Add Stage 1B shared domain foundation.

Revision ID: 0003_stage1b_domain_foundation
Revises: 0002_phase3_documents
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_stage1b_domain_foundation"
down_revision: Union[str, Sequence[str], None] = "0002_phase3_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamps(table: str) -> list[sa.Column]:
	return [
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
	]


def upgrade() -> None:
	op.create_table(
		"intelligence_requests",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("request_type", sa.String(64), nullable=False),
		sa.Column("input_text", sa.Text()),
		sa.Column("input_metadata", sa.JSON()),
		sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_intelligence_requests_user_id", "intelligence_requests", ["user_id"])

	op.create_table(
		"analysis_runs",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("request_id", sa.Uuid(), nullable=False),
		sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
		sa.Column("provider_identifier", sa.String(128)),
		sa.Column("started_at", sa.DateTime(timezone=True)),
		sa.Column("completed_at", sa.DateTime(timezone=True)),
		sa.Column("error_code", sa.String(64)),
		sa.Column("error_summary", sa.String(500)),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["request_id"], ["intelligence_requests.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_analysis_runs_user_id", "analysis_runs", ["user_id"])
	op.create_index("ix_analysis_runs_request_id", "analysis_runs", ["request_id"])

	op.create_table(
		"intelligence_insights",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("analysis_run_id", sa.Uuid(), nullable=False),
		sa.Column("title", sa.String(200), nullable=False),
		sa.Column("description", sa.Text(), nullable=False),
		sa.Column("category", sa.String(32), nullable=False),
		sa.Column("importance", sa.Integer()),
		sa.Column("confidence", sa.Float()),
		sa.Column("uncertainty", sa.Float()),
		sa.Column("status", sa.String(32), nullable=False, server_default="active"),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="ck_insights_confidence_range"),
		sa.CheckConstraint("uncertainty IS NULL OR (uncertainty >= 0 AND uncertainty <= 1)", name="ck_insights_uncertainty_range"),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_intelligence_insights_user_id", "intelligence_insights", ["user_id"])
	op.create_index("ix_intelligence_insights_analysis_run_id", "intelligence_insights", ["analysis_run_id"])

	op.create_table(
		"context_references",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("analysis_run_id", sa.Uuid(), nullable=False),
		sa.Column("reference_type", sa.String(32), nullable=False),
		sa.Column("reference_id", sa.Uuid(), nullable=False),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_context_references_user_id", "context_references", ["user_id"])

	op.create_table(
		"user_feedback",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("insight_id", sa.Uuid(), nullable=False),
		sa.Column("value", sa.String(32), nullable=False),
		sa.Column("correction", sa.Text()),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["insight_id"], ["intelligence_insights.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_user_feedback_user_id", "user_feedback", ["user_id"])

	op.create_table(
		"evidence_sources",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("document_id", sa.Uuid()),
		sa.Column("analysis_run_id", sa.Uuid()),
		sa.Column("source_type", sa.String(32), nullable=False),
		sa.Column("source_reference", sa.String(500), nullable=False),
		sa.Column("page_number", sa.Integer()),
		sa.Column("section_reference", sa.String(200)),
		sa.Column("excerpt", sa.Text()),
		sa.Column("verification_status", sa.String(32), nullable=False, server_default="unverified"),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.CheckConstraint("document_id IS NOT NULL OR analysis_run_id IS NOT NULL", name="ck_evidence_source_parent"),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_evidence_sources_user_id", "evidence_sources", ["user_id"])

	op.create_table(
		"goals",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("title", sa.String(200), nullable=False),
		sa.Column("description", sa.Text()),
		sa.Column("status", sa.String(32), nullable=False, server_default="active"),
		sa.Column("target_date", sa.DateTime(timezone=True)),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.Column("completed_at", sa.DateTime(timezone=True)),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_goals_user_id", "goals", ["user_id"])

	op.create_table(
		"tasks",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("action_plan_id", sa.Uuid()),
		sa.Column("goal_id", sa.Uuid()),
		sa.Column("title", sa.String(200), nullable=False),
		sa.Column("description", sa.Text()),
		sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
		sa.Column("priority", sa.String(16), nullable=False, server_default="medium"),
		sa.Column("due_at", sa.DateTime(timezone=True)),
		sa.Column("estimated_duration_minutes", sa.Integer()),
		sa.Column("completed_at", sa.DateTime(timezone=True)),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.CheckConstraint("estimated_duration_minutes IS NULL OR estimated_duration_minutes > 0", name="ck_tasks_duration_positive"),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["action_plan_id"], ["action_plans.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="RESTRICT"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_tasks_user_id", "tasks", ["user_id"])
	op.create_index("ix_tasks_action_plan_id", "tasks", ["action_plan_id"])

	op.create_table(
		"task_dependencies",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("task_id", sa.Uuid(), nullable=False),
		sa.Column("depends_on_task_id", sa.Uuid(), nullable=False),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
		sa.CheckConstraint("task_id <> depends_on_task_id", name="ck_task_dependency_not_self"),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
		sa.ForeignKeyConstraint(["depends_on_task_id"], ["tasks.id"], ondelete="CASCADE"),
		sa.PrimaryKeyConstraint("id"),
		sa.UniqueConstraint("user_id", "task_id", "depends_on_task_id", name="uq_task_dependency"),
	)
	op.create_index("ix_task_dependencies_user_id", "task_dependencies", ["user_id"])

	op.create_table(
		"goal_milestones",
		sa.Column("id", sa.Uuid(), nullable=False),
		sa.Column("user_id", sa.Uuid(), nullable=False),
		sa.Column("goal_id", sa.Uuid(), nullable=False),
		sa.Column("title", sa.String(200), nullable=False),
		sa.Column("description", sa.Text()),
		sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
		sa.Column("target_date", sa.DateTime(timezone=True)),
		sa.Column("completed_at", sa.DateTime(timezone=True)),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
		sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_goal_milestones_user_id", "goal_milestones", ["user_id"])
	op.create_index("ix_goal_milestones_goal_id", "goal_milestones", ["goal_id"])


def downgrade() -> None:
	op.drop_index("ix_goal_milestones_goal_id", table_name="goal_milestones")
	op.drop_index("ix_goal_milestones_user_id", table_name="goal_milestones")
	op.drop_table("goal_milestones")
	op.drop_index("ix_task_dependencies_user_id", table_name="task_dependencies")
	op.drop_table("task_dependencies")
	op.drop_index("ix_tasks_action_plan_id", table_name="tasks")
	op.drop_index("ix_tasks_user_id", table_name="tasks")
	op.drop_table("tasks")
	op.drop_index("ix_goals_user_id", table_name="goals")
	op.drop_table("goals")
	op.drop_index("ix_evidence_sources_user_id", table_name="evidence_sources")
	op.drop_table("evidence_sources")
	op.drop_index("ix_user_feedback_user_id", table_name="user_feedback")
	op.drop_table("user_feedback")
	op.drop_index("ix_context_references_user_id", table_name="context_references")
	op.drop_table("context_references")
	op.drop_index("ix_intelligence_insights_analysis_run_id", table_name="intelligence_insights")
	op.drop_index("ix_intelligence_insights_user_id", table_name="intelligence_insights")
	op.drop_table("intelligence_insights")
	op.drop_index("ix_analysis_runs_request_id", table_name="analysis_runs")
	op.drop_index("ix_analysis_runs_user_id", table_name="analysis_runs")
	op.drop_table("analysis_runs")
	op.drop_index("ix_intelligence_requests_user_id", table_name="intelligence_requests")
	op.drop_table("intelligence_requests")
