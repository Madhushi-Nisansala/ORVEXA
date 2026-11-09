from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Task(Base):
	__tablename__ = "tasks"
	__table_args__ = (
		Index("ix_tasks_user_id", "user_id"),
		Index("ix_tasks_action_plan_id", "action_plan_id"),
		Index("ix_tasks_search_scope", "user_id", "status", "created_at"),
		CheckConstraint("estimated_duration_minutes IS NULL OR estimated_duration_minutes > 0", name="ck_tasks_duration_positive"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	action_plan_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("action_plans.id", ondelete="RESTRICT"))
	goal_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("goals.id", ondelete="RESTRICT"))
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[str | None] = mapped_column(Text)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", server_default="pending")
	priority: Mapped[str] = mapped_column(String(16), nullable=False, default="medium", server_default="medium")
	due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer)
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class TaskDependency(Base):
	__tablename__ = "task_dependencies"
	__table_args__ = (
		UniqueConstraint("user_id", "task_id", "depends_on_task_id", name="uq_task_dependency"),
		Index("ix_task_dependencies_user_id", "user_id"),
		CheckConstraint("task_id <> depends_on_task_id", name="ck_task_dependency_not_self"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	task_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
	depends_on_task_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Goal(Base):
	__tablename__ = "goals"
	__table_args__ = (
		Index("ix_goals_user_id", "user_id"),
		Index("ix_goals_search_scope", "user_id", "status", "created_at"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[str | None] = mapped_column(Text)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", server_default="active")
	target_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class GoalMilestone(Base):
	__tablename__ = "goal_milestones"
	__table_args__ = (Index("ix_goal_milestones_user_id", "user_id"), Index("ix_goal_milestones_goal_id", "goal_id"))

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	goal_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[str | None] = mapped_column(Text)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", server_default="pending")
	target_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
