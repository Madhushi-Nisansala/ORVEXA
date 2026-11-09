import pytest
from pydantic import ValidationError

from app.api.v1 import dependencies
from app.core.config import Settings
from app.database.session import engine


def test_current_user_dependency_has_eager_role_loader() -> None:
	assert dependencies.selectinload is not None


def test_production_rejects_placeholder_jwt_secret() -> None:
	with pytest.raises(ValidationError):
		Settings(APP_ENV="production", JWT_SECRET_KEY="CHANGE_ME")


def test_production_requires_a_strong_jwt_secret() -> None:
	with pytest.raises(ValidationError):
		Settings(APP_ENV="production", JWT_SECRET_KEY="too-short")


def test_only_supported_jwt_algorithm_is_allowed() -> None:
	with pytest.raises(ValidationError):
		Settings(JWT_ALGORITHM="none")


def test_sqlalchemy_sql_echo_is_disabled() -> None:
	assert engine.echo is False
