from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.modules.actions.models import Goal, GoalMilestone, Task
from app.modules.actions.schemas import (
	GoalCreate,
	GoalMilestoneCreate,
	GoalMilestoneResponse,
	GoalMilestoneStatusUpdate,
	GoalMilestoneUpdate,
	GoalResponse,
	GoalStatusContract,
	GoalUpdate,
	TaskCreate,
	TaskDependencyCreate,
	TaskDependencyResponse,
	TaskDependencyTarget,
	TaskResponse,
	TaskStatusUpdate,
	TaskUpdate,
)
from app.shared.enums import TaskPriority, TaskStatus
from app.modules.actions.services import DependencyCycleError, GoalService, OwnershipError, TaskService

router = APIRouter(tags=["actions"])


def task_service(db: AsyncSession) -> TaskService:
	return TaskService(db)


def goal_service(db: AsyncSession) -> GoalService:
	return GoalService(db)


def not_found(detail: str) -> HTTPException:
	return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


async def owned_task(task_id: UUID, user_id: UUID, db: AsyncSession) -> Task:
	task = await task_service(db).tasks.get_owned(task_id, user_id)
	if task is None:
		raise not_found("Task not found")
	return task


async def owned_goal(goal_id: UUID, user_id: UUID, db: AsyncSession) -> Goal:
	goal = await goal_service(db).goals.get_owned(goal_id, user_id)
	if goal is None:
		raise not_found("Goal not found")
	return goal


async def owned_milestone(milestone_id: UUID, goal_id: UUID, user_id: UUID, db: AsyncSession) -> GoalMilestone:
	milestone = await goal_service(db).goals.get_milestone(milestone_id, user_id)
	if milestone is None or milestone.goal_id != goal_id:
		raise not_found("Milestone not found")
	return milestone


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
	payload: TaskCreate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> Task:
	try:
		task = await task_service(db).create_task(user.id, payload)
		await db.commit()
		await db.refresh(task)
		return task
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
	response: Response,
	limit: int = Query(50, ge=1, le=100),
	offset: int = Query(0, ge=0),
	status_filter: TaskStatus | None = Query(default=None, alias="status"),
	priority: TaskPriority | None = None,
	search: str | None = Query(default=None, min_length=1, max_length=200),
	sort_by: str = Query(default="created_at", pattern="^(created_at|updated_at|due_at|title|priority|status)$"),
	sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> list[Task]:
	service = task_service(db)
	items = await service.tasks.list_owned(
		user.id,
		limit,
		offset,
		status=status_filter.value if status_filter else None,
		priority=priority.value if priority else None,
		search=search,
		sort_by=sort_by,
		descending=sort_order == "desc",
	)
	response.headers["X-Total-Count"] = str(await service.tasks.count_owned(user.id, status=status_filter.value if status_filter else None, priority=priority.value if priority else None, search=search))
	return items


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Task:
	return await owned_task(task_id, user.id, db)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
	task_id: UUID,
	payload: TaskUpdate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> Task:
	try:
		task = await task_service(db).update_task(user.id, task_id, payload.model_dump(exclude_unset=True))
		await db.commit()
		await db.refresh(task)
		return task
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
	task_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> Response:
	try:
		await task_service(db).delete_task(user.id, task_id)
		await db.commit()
		return Response(status_code=status.HTTP_204_NO_CONTENT)
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc


@router.post("/tasks/{task_id}/status", response_model=TaskResponse)
async def change_task_status(
	task_id: UUID,
	payload: TaskStatusUpdate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> Task:
	try:
		task = await task_service(db).change_status(user.id, task_id, payload.status)
		await db.commit()
		await db.refresh(task)
		return task
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc
	except ValueError as exc:
		await db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/dependencies", response_model=TaskDependencyResponse, status_code=status.HTTP_201_CREATED)
async def add_task_dependency(
	task_id: UUID,
	payload: TaskDependencyTarget,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> object:
	try:
		dependency = await task_service(db).add_dependency(
			user.id,
			TaskDependencyCreate(task_id=task_id, depends_on_task_id=payload.depends_on_task_id),
		)
		await db.commit()
		await db.refresh(dependency)
		return dependency
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc
	except DependencyCycleError as exc:
		await db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
	except ValueError as exc:
		await db.rollback()
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
	except IntegrityError as exc:
		await db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dependency already exists") from exc


@router.get("/tasks/{task_id}/dependencies", response_model=list[TaskDependencyResponse])
async def list_task_dependencies(
	task_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> list[object]:
	await owned_task(task_id, user.id, db)
	return await task_service(db).tasks.list_dependencies(task_id, user.id)


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
	payload: GoalCreate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> Goal:
	goal = await goal_service(db).create_goal(user.id, payload)
	await db.commit()
	await db.refresh(goal)
	return goal


@router.get("/goals", response_model=list[GoalResponse])
async def list_goals(
	limit: int = Query(50, ge=1, le=100),
	offset: int = Query(0, ge=0),
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> list[Goal]:
	return await goal_service(db).goals.list_owned(user.id, limit, offset)


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(goal_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Goal:
	return await owned_goal(goal_id, user.id, db)


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
	goal_id: UUID,
	payload: GoalUpdate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> Goal:
	try:
		goal = await goal_service(db).update_goal(user.id, goal_id, payload.model_dump(exclude_unset=True))
		await db.commit()
		await db.refresh(goal)
		return goal
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc


@router.post("/goals/{goal_id}/status", response_model=GoalResponse)
async def change_goal_status(
	goal_id: UUID,
	payload: GoalStatusContract,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> Goal:
	try:
		goal = await goal_service(db).change_status(user.id, goal_id, payload.status)
		await db.commit()
		await db.refresh(goal)
		return goal
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc


@router.post("/goals/{goal_id}/milestones", response_model=GoalMilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
	goal_id: UUID,
	payload: GoalMilestoneCreate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> GoalMilestone:
	if payload.goal_id != goal_id:
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Goal ID does not match the path")
	try:
		milestone = await goal_service(db).create_milestone(user.id, payload)
		await db.commit()
		await db.refresh(milestone)
		return milestone
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc


@router.get("/goals/{goal_id}/milestones", response_model=list[GoalMilestoneResponse])
async def list_milestones(
	goal_id: UUID,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> list[GoalMilestone]:
	await owned_goal(goal_id, user.id, db)
	return await goal_service(db).goals.list_milestones(goal_id, user.id)


@router.patch("/goals/{goal_id}/milestones/{milestone_id}", response_model=GoalMilestoneResponse)
async def update_milestone(
	goal_id: UUID,
	milestone_id: UUID,
	payload: GoalMilestoneUpdate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> GoalMilestone:
	await owned_milestone(milestone_id, goal_id, user.id, db)
	try:
		milestone = await goal_service(db).update_milestone(
			user.id, milestone_id, payload.model_dump(exclude_unset=True)
		)
		await db.commit()
		await db.refresh(milestone)
		return milestone
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc


@router.post("/goals/{goal_id}/milestones/{milestone_id}/status", response_model=GoalMilestoneResponse)
async def change_milestone_status(
	goal_id: UUID,
	milestone_id: UUID,
	payload: GoalMilestoneStatusUpdate,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> GoalMilestone:
	await owned_milestone(milestone_id, goal_id, user.id, db)
	if payload.status is None and payload.completed is None:
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Status or completed is required")
	try:
		milestone = await goal_service(db).change_milestone_status(
			user.id, milestone_id, payload.status or "pending", payload.completed
		)
		await db.commit()
		await db.refresh(milestone)
		return milestone
	except OwnershipError as exc:
		await db.rollback()
		raise not_found(str(exc)) from exc
