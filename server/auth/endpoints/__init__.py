from .group import router as group_router
from .role import router as role_router
from .user import router as user_router
from .workspace import router as workspace_router
from .app import router as app_router
from .page import router as page_router
from fastapi import APIRouter


premium_router = APIRouter()
premium_router.include_router(group_router)
premium_router.include_router(role_router)
premium_router.include_router(user_router)
premium_router.include_router(workspace_router)
premium_router.include_router(app_router)
premium_router.include_router(page_router)
