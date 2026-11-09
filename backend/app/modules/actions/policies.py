from app.shared.enums import TaskStatus


_ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
	TaskStatus.pending: {TaskStatus.in_progress, TaskStatus.cancelled},
	TaskStatus.in_progress: {TaskStatus.pending, TaskStatus.completed, TaskStatus.cancelled},
	TaskStatus.completed: set(),
	TaskStatus.cancelled: {TaskStatus.pending},
}


def validate_task_transition(current: TaskStatus, requested: TaskStatus) -> None:
	if requested not in _ALLOWED_TRANSITIONS[current]:
		raise ValueError(f"Invalid task status transition: {current} -> {requested}")
