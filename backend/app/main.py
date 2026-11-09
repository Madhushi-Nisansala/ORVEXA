from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.endpoints.system import router as system_router
from app.core.config import get_settings
from app.core.exceptions import unhandled_exception_handler
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings)

app = FastAPI(
	title=f'{settings.app_name} API',
	description='ORVEXA project foundation API.',
	version=settings.app_version,
	docs_url='/docs' if settings.app_env.lower() not in {'production', 'staging'} else None,
	redoc_url='/redoc' if settings.app_env.lower() not in {'production', 'staging'} else None,
)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins,
	allow_credentials=True,
	allow_methods=['GET', 'POST', 'DELETE', 'PATCH', 'OPTIONS'],
	allow_headers=['Authorization', 'Content-Type'],
)


@app.middleware("http")
async def security_headers(request, call_next):
	response = await call_next(request)
	response.headers["X-Content-Type-Options"] = "nosniff"
	response.headers["X-Frame-Options"] = "DENY"
	response.headers["Referrer-Policy"] = "no-referrer"
	response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
	if settings.app_env.lower() in {"production", "staging"}:
		response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
	return response


app.include_router(system_router)
app.include_router(api_router, prefix=settings.api_v1_prefix)
