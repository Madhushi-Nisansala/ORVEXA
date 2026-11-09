from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.actions.policies import validate_task_transition
from app.modules.actions.schemas import TaskDependencyCreate
from app.modules.actions.services import would_create_cycle
from app.modules.evidence.schemas import EvidenceSourceCreate
from app.modules.intelligence.schemas import InsightCreate
from app.shared.enums import TaskStatus
from app.shared.pagination import PaginationParams


def test_pagination_is_bounded() -> None:
	assert PaginationParams(limit=100, offset=0).limit == 100
	with pytest.raises(ValidationError):
		PaginationParams(limit=101)


def test_insight_confidence_is_optional_and_bounded() -> None:
	base = {
		"analysis_run_id": uuid4(),
		"title": "Finding",
		"description": "Description",
		"category": "finding",
	}
	assert InsightCreate(**base).confidence is None
	with pytest.raises(ValidationError):
		InsightCreate(**base, confidence=1.1)


def test_evidence_requires_a_validated_parent_reference() -> None:
	with pytest.raises(ValidationError):
		EvidenceSourceCreate(source_type="document", source_reference="page 1")
	assert EvidenceSourceCreate(
		document_id=uuid4(), source_type="document", source_reference="page 1"
	).document_id is not None


def test_self_dependency_is_rejected_by_contract() -> None:
	task_id = uuid4()
	with pytest.raises(ValidationError):
		TaskDependencyCreate(task_id=task_id, depends_on_task_id=task_id)


def test_task_status_transitions_are_explicit() -> None:
	validate_task_transition(TaskStatus.pending, TaskStatus.in_progress)
	with pytest.raises(ValueError):
		validate_task_transition(TaskStatus.completed, TaskStatus.pending)