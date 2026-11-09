from fastapi import APIRouter

from app.api.v1.endpoints.system import router as system_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.intelligence import router as intelligence_router
from app.api.v1.endpoints.context import router as context_router
from app.api.v1.endpoints.actions import router as actions_router
from app.api.v1.endpoints.search import router as search_router

api_router = APIRouter()
api_router.include_router(system_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(admin_router)
api_router.include_router(documents_router)
api_router.include_router(intelligence_router)
api_router.include_router(context_router)
api_router.include_router(actions_router)
api_router.include_router(search_router)
