from enum import StrEnum


class ProcessingStatus(StrEnum):
	pending = "pending"
	queued = "queued"
	running = "running"
	completed = "completed"
	failed = "failed"


class AnalysisStatus(StrEnum):
	pending = "pending"
	running = "running"
	completed = "completed"
	failed = "failed"


class InsightCategory(StrEnum):
	summary = "summary"
	finding = "finding"
	recommendation = "recommendation"
	risk = "risk"


class VerificationStatus(StrEnum):
	unverified = "unverified"
	verified = "verified"
	rejected = "rejected"


class FeedbackValue(StrEnum):
	helpful = "helpful"
	not_helpful = "not_helpful"
	inaccurate = "inaccurate"
	incomplete = "incomplete"
	dismissed = "dismissed"
	corrected = "corrected"


class ApprovalStatus(StrEnum):
	proposed = "proposed"
	approved = "approved"
	rejected = "rejected"
	dismissed = "dismissed"


class TaskStatus(StrEnum):
	pending = "pending"
	in_progress = "in_progress"
	completed = "completed"
	cancelled = "cancelled"


class TaskPriority(StrEnum):
	low = "low"
	medium = "medium"
	high = "high"
	urgent = "urgent"


class GoalStatus(StrEnum):
	active = "active"
	completed = "completed"
	paused = "paused"
	archived = "archived"


class PlanStatus(StrEnum):
	proposed = "proposed"
	approved = "approved"
	active = "active"
	completed = "completed"
	cancelled = "cancelled"
