from fastapi import APIRouter, Depends

from app.api.v1.dependencies import require_roles
from app.database.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/example")
async def admin_example(_: User = Depends(require_roles("admin"))) -> dict[str, str]:
	return {"message": "Admin access granted"}
