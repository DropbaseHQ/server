from fastapi import APIRouter, Depends

from server.controllers.sources import get_sources
from server.auth.dependency import EnforceUserAppPermissions

router = APIRouter(
    prefix="/sources",
    tags=["sources"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", dependencies=[Depends(EnforceUserAppPermissions(action="use"))])
async def get_workspace_sources():
    sources = get_sources()
    return {"sources": list(sources.keys())}
