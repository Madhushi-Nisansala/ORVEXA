from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import logging

from app.core.config import get_settings
from app.database.session import check_database_connection
from app.schemas.system import HealthResponse, ReadinessResponse, RootResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["system"])


@router.get("/", response_model=RootResponse)
async def root() -> RootResponse:
	settings = get_settings()
	return RootResponse(
		application=settings.app_name,
		version=settings.app_version,
		status="operational",
		api_prefix=settings.api_v1_prefix,
	)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse | JSONResponse:
	settings = get_settings()
	connected = await check_database_connection()
	response = HealthResponse(
		status="healthy" if connected else "degraded",
		application=settings.app_name,
		version=settings.app_version,
		database="connected" if connected else "unavailable",
	)
	if not connected:
		return JSONResponse(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			content=response.model_dump(),
		)
	return response


@router.get("/ready", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse | JSONResponse:
	connected = await check_database_connection()
	response = ReadinessResponse(
		status="ready" if connected else "not_ready",
		checks={"database": "connected" if connected else "unavailable"},
	)
	if not connected:
		return JSONResponse(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			content=response.model_dump(),
		)
	return response
