from fastapi import APIRouter

from server.controllers.sources import get_sources

router = APIRouter(prefix="/sources", tags=["sources"], responses={404: {"description": "Not found"}})


@router.get("/")
async def get_workspace_sources():
    sources = get_sources()
    return {"sources": list(sources.keys())}
