from fastapi import APIRouter

from server.constants import DEFAULT_RESPONSES
from server.controllers.sources import get_source_name_type

router = APIRouter(prefix="/sources", tags=["sources"], responses=DEFAULT_RESPONSES)


@router.get("/")
async def get_workspace_sources():
    return get_source_name_type()
