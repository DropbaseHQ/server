from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.controllers.sync import sync_with_dropbase

router = APIRouter(
    prefix="/worker_workspace",
    tags=["workspace"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_workspace(router: DropbaseRouter = Depends(get_dropbase_router)) -> dict:
    response = router.auth.get_worker_workspace()
    workspace_info = response.json()
    sync_with_dropbase(router=router)
    return workspace_info


@router.post("/sync")
async def sync_workspace(router: DropbaseRouter = Depends(get_dropbase_router)) -> dict:
    response = router.auth.sync_worker_workspace()
    workspace_info = response.json()
    return workspace_info
