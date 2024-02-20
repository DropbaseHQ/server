from fastapi import APIRouter, Depends
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(
    prefix="/worker_workspace",
    tags=["workspace"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_workspace(router: DropbaseRouter = Depends(get_dropbase_router)) -> dict:
    response = router.auth.get_worker_workspace()
    workspace_info = response.json()
    return workspace_info
