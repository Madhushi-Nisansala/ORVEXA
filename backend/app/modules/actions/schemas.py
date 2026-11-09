from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.shared.enums import GoalStatus, PlanStatus, TaskPriority, TaskStatus


class TaskCreate(BaseModel):
	action_plan_id: UUID | None = None
	goal_id: UUID | None = None
	title: str = Field(min_length=1, max_length=200)
	description: str | None = None
	priority: TaskPriority = TaskPriority.medium
	due_at: datetime | None = None
	estimated_duration_minutes: int | None = Field(default=None, gt=0)


class TaskUpdate(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=200)
	description: str | None = None
	priority: TaskPriority | None = None
	due_at: datetime | None = None
	estimated_duration_minutes: int | None = Field(default=None, gt=0)


class TaskStatusUpdate(BaseModel):
	status: TaskStatus


class TaskDependencyCreate(BaseModel):
	task_id: UUID
	depends_on_task_id: UUID

	@model_validator(mode="after")
	def reject_self_dependency(self) -> "TaskDependencyCreate":
		if self.task_id == self.depends_on_task_id:
			raise ValueError("A task cannot depend on itself")
		return self


class TaskDependencyTarget(BaseModel):
	depends_on_task_id: UUID


class TaskResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	user_id: UUID
	action_plan_id: UUID | None
	goal_id: UUID | None
	title: str
	description: str | None
	status: TaskStatus
	priority: TaskPriority
	due_at: datetime | None
	estimated_duration_minutes: int | None
	completed_at: datetime | None
	created_at: datetime
	updated_at: datetime


class TaskDependencyResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	task_id: UUID
	depends_on_task_id: UUID
	created_at: datetime


class GoalCreate(BaseModel):
	title: str = Field(min_length=1, max_length=200)
	description: str | None = None
	target_date: datetime | None = None


class GoalUpdate(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=200)
	description: str | None = None
	target_date: datetime | None = None


class GoalResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	user_id: UUID
	title: str
	description: str | None
	status: GoalStatus
	target_date: datetime | None
	created_at: datetime
	updated_at: datetime
	completed_at: datetime | None


class GoalMilestoneCreate(BaseModel):
	goal_id: UUID
	title: str = Field(min_length=1, max_length=200)
	description: str | None = None
	target_date: datetime | None = None


class GoalMilestoneUpdate(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=200)
	description: str | None = None
	target_date: datetime | None = None


class GoalMilestoneStatusUpdate(BaseModel):
	status: str | None = Field(default=None, min_length=1, max_length=32)
	completed: bool | None = None


class GoalMilestoneResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	user_id: UUID
	goal_id: UUID
	title: str
	description: str | None
	status: str
	target_date: datetime | None
	completed_at: datetime | None


class ActionPlanContract(BaseModel):
	status: PlanStatus = PlanStatus.proposed


class GoalStatusContract(BaseModel):
	status: GoalStatus
