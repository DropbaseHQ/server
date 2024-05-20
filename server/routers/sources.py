from fastapi import APIRouter

from server.controllers.sources import get_source_name_type

router = APIRouter(prefix="/sources", tags=["sources"], responses={404: {"description": "Not found"}})


@router.get("/")
async def get_workspace_sources():
    return get_source_name_type()
