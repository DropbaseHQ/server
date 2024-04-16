from .group import router as group_router
from .role import router as role_router
from .token import router as token_router
from .user import router as user_router
from .workspace import router as workspace_router
from .url_mapping import router as url_mapping_router
from .app import router as app_router
from fastapi import APIRouter


premium_router = APIRouter()
premium_router.include_router(group_router)
premium_router.include_router(role_router)
premium_router.include_router(token_router)
premium_router.include_router(user_router)
premium_router.include_router(workspace_router)
premium_router.include_router(url_mapping_router)
premium_router.include_router(app_router)
