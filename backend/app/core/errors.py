from fastapi import Request
from fastapi.responses import JSONResponse


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
	"""Return a safe error response without leaking internal exception details."""

	return JSONResponse(
		status_code=500,
		content={"error": {"code": "internal_error", "message": "An unexpected error occurred."}},
	)
