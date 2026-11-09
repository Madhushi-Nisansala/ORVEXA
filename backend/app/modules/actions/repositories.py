from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.actions.models import Goal, GoalMilestone, Task, TaskDependency


class TaskRepository:
	def __init__(self, session: AsyncSession) -> None:
		self.session = session

	async def get_owned(self, task_id: UUID, user_id: UUID) -> Task | None:
		result = await self.session.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
		return result.scalar_one_or_none()

	async def list_owned(
		self,
		user_id: UUID,
		limit: int,
		offset: int,
		*,
		status: str | None = None,
		priority: str | None = None,
		search: str | None = None,
		sort_by: str = "created_at",
		descending: bool = True,
	) -> list[Task]:
		filters = [Task.user_id == user_id]
		if status is not None:
			filters.append(Task.status == status)
		if priority is not None:
			filters.append(Task.priority == priority)
		if search is not None:
			pattern = f"%{search}%"
			filters.append(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))
		column = getattr(Task, sort_by)
		result = await self.session.execute(
			select(Task).where(*filters).order_by((column.desc() if descending else column.asc()), Task.id).limit(limit).offset(offset)
		)
		return list(result.scalars())

	async def count_owned(
		self, user_id: UUID, *, status: str | None = None, priority: str | None = None, search: str | None = None
	) -> int:
		filters = [Task.user_id == user_id]
		if status is not None:
			filters.append(Task.status == status)
		if priority is not None:
			filters.append(Task.priority == priority)
		if search is not None:
			pattern = f"%{search}%"
			filters.append(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))
		return int(await self.session.scalar(select(func.count()).select_from(Task).where(*filters)) or 0)

	async def delete_owned(self, task_id: UUID, user_id: UUID) -> bool:
		task = await self.get_owned(task_id, user_id)
		if task is None:
			return False
		await self.session.delete(task)
		return True

	async def list_dependencies(self, task_id: UUID, user_id: UUID) -> list[TaskDependency]:
		result = await self.session.execute(
			select(TaskDependency)
			.where(TaskDependency.task_id == task_id, TaskDependency.user_id == user_id)
			.order_by(TaskDependency.created_at)
		)
		return list(result.scalars())

	async def get_dependency(self, dependency_id: UUID, user_id: UUID) -> TaskDependency | None:
		return await self.session.scalar(
			select(TaskDependency).where(TaskDependency.id == dependency_id, TaskDependency.user_id == user_id)
		)


class GoalRepository:
	def __init__(self, session: AsyncSession) -> None:
		self.session = session

	async def get_owned(self, goal_id: UUID, user_id: UUID) -> Goal | None:
		return await self.session.scalar(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))

	async def list_owned(self, user_id: UUID, limit: int, offset: int) -> list[Goal]:
		result = await self.session.execute(
			select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc()).limit(limit).offset(offset)
		)
		return list(result.scalars())

	async def list_milestones(self, goal_id: UUID, user_id: UUID) -> list[GoalMilestone]:
		result = await self.session.execute(
			select(GoalMilestone)
			.where(GoalMilestone.goal_id == goal_id, GoalMilestone.user_id == user_id)
			.order_by(GoalMilestone.target_date, GoalMilestone.created_at)
		)
		return list(result.scalars())

	async def get_milestone(self, milestone_id: UUID, user_id: UUID) -> GoalMilestone | None:
		return await self.session.scalar(
			select(GoalMilestone).where(GoalMilestone.id == milestone_id, GoalMilestone.user_id == user_id)
		)
