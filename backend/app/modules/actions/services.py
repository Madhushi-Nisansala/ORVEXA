from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.actions.models import Goal, GoalMilestone, Task, TaskDependency
from app.modules.actions.policies import validate_task_transition
from app.modules.actions.repositories import GoalRepository, TaskRepository
from app.modules.actions.schemas import (
	GoalCreate,
	GoalMilestoneCreate,
	TaskCreate,
	TaskDependencyCreate,
)
from app.shared.enums import GoalStatus, TaskStatus


class OwnershipError(ValueError):
	pass


class DependencyCycleError(ValueError):
	pass


def would_create_cycle(
	edges: list[tuple[UUID, UUID]], task_id: UUID, depends_on_task_id: UUID
) -> bool:
	graph: dict[UUID, set[UUID]] = {}
	for source, target in edges:
		graph.setdefault(source, set()).add(target)
	graph.setdefault(task_id, set()).add(depends_on_task_id)
	pending = [depends_on_task_id]
	visited: set[UUID] = set()
	while pending:
		current = pending.pop()
		if current == task_id:
			return True
		if current in visited:
			continue
		visited.add(current)
		pending.extend(graph.get(current, ()))
	return False


class TaskService:
	def __init__(self, session: AsyncSession) -> None:
		self.session = session
		self.tasks = TaskRepository(session)

	async def create_task(self, user_id: UUID, data: TaskCreate) -> Task:
		if data.goal_id is not None and await self.session.scalar(
			select(Goal).where(Goal.id == data.goal_id, Goal.user_id == user_id)
		) is None:
			raise OwnershipError("The goal must belong to the authenticated user")
		task = Task(user_id=user_id, **data.model_dump())
		self.session.add(task)
		await self.session.flush()
		return task

	async def delete_task(self, user_id: UUID, task_id: UUID) -> None:
		if not await self.tasks.delete_owned(task_id, user_id):
			raise OwnershipError("Task not found")
		await self.session.flush()

	async def _creates_cycle(self, user_id: UUID, task_id: UUID, depends_on_task_id: UUID) -> bool:
		edges = await self.session.execute(
			select(TaskDependency.task_id, TaskDependency.depends_on_task_id).where(TaskDependency.user_id == user_id)
		)
		return would_create_cycle(list(edges), task_id, depends_on_task_id)

	async def add_dependency(self, user_id: UUID, data: TaskDependencyCreate) -> TaskDependency:
		if data.task_id == data.depends_on_task_id:
			raise ValueError("A task cannot depend on itself")
		task = await self.tasks.get_owned(data.task_id, user_id)
		dependency = await self.tasks.get_owned(data.depends_on_task_id, user_id)
		if task is None or dependency is None:
			raise OwnershipError("Both tasks must belong to the authenticated user")
		if await self._creates_cycle(user_id, data.task_id, data.depends_on_task_id):
			raise DependencyCycleError("The task dependency would create a cycle")
		row = TaskDependency(user_id=user_id, task_id=data.task_id, depends_on_task_id=data.depends_on_task_id)
		self.session.add(row)
		await self.session.flush()
		return row

	async def change_status(self, user_id: UUID, task_id: UUID, requested: TaskStatus) -> Task:
		task = await self.tasks.get_owned(task_id, user_id)
		if task is None:
			raise OwnershipError("Task not found")
		validate_task_transition(TaskStatus(task.status), requested)
		task.status = requested.value
		task.completed_at = datetime.now(timezone.utc) if requested is TaskStatus.completed else None
		await self.session.flush()
		return task

	async def update_task(self, user_id: UUID, task_id: UUID, values: dict[str, object]) -> Task:
		task = await self.tasks.get_owned(task_id, user_id)
		if task is None:
			raise OwnershipError("Task not found")
		for key, value in values.items():
			setattr(task, key, value)
		await self.session.flush()
		return task


class GoalService:
	def __init__(self, session: AsyncSession) -> None:
		self.session = session
		self.goals = GoalRepository(session)

	async def create_goal(self, user_id: UUID, data: GoalCreate) -> Goal:
		goal = Goal(user_id=user_id, **data.model_dump())
		self.session.add(goal)
		await self.session.flush()
		return goal

	async def update_goal(self, user_id: UUID, goal_id: UUID, values: dict[str, object]) -> Goal:
		goal = await self.goals.get_owned(goal_id, user_id)
		if goal is None:
			raise OwnershipError("Goal not found")
		for key, value in values.items():
			setattr(goal, key, value)
		await self.session.flush()
		return goal

	async def change_status(self, user_id: UUID, goal_id: UUID, requested: GoalStatus) -> Goal:
		goal = await self.goals.get_owned(goal_id, user_id)
		if goal is None:
			raise OwnershipError("Goal not found")
		goal.status = requested.value
		goal.completed_at = datetime.now(timezone.utc) if requested is GoalStatus.completed else None
		await self.session.flush()
		return goal

	async def create_milestone(self, user_id: UUID, data: GoalMilestoneCreate) -> GoalMilestone:
		if await self.goals.get_owned(data.goal_id, user_id) is None:
			raise OwnershipError("Goal not found")
		milestone = GoalMilestone(user_id=user_id, **data.model_dump())
		self.session.add(milestone)
		await self.session.flush()
		return milestone

	async def update_milestone(self, user_id: UUID, milestone_id: UUID, values: dict[str, object]) -> GoalMilestone:
		milestone = await self.goals.get_milestone(milestone_id, user_id)
		if milestone is None:
			raise OwnershipError("Milestone not found")
		for key, value in values.items():
			setattr(milestone, key, value)
		await self.session.flush()
		return milestone

	async def change_milestone_status(
		self, user_id: UUID, milestone_id: UUID, requested: str, completed: bool | None
	) -> GoalMilestone:
		milestone = await self.goals.get_milestone(milestone_id, user_id)
		if milestone is None:
			raise OwnershipError("Milestone not found")
		if completed is True:
			requested = "completed"
		elif completed is False:
			requested = "pending"
		milestone.status = requested
		milestone.completed_at = datetime.now(timezone.utc) if requested == "completed" else None
		await self.session.flush()
		return milestone

