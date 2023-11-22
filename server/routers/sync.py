from fastapi import APIRouter, Response, Depends

from server.schemas.sync import GetTableColumns, SyncComponents, SyncTableColumns
from server.worker.python_subprocess import run_process_task
from server.worker.sync import sync_components, sync_page
from server.controllers.sync import get_page_state_context
from server.requests.dropbase_router import (
    get_access_cookies,
    AccessCookies,
    DropbaseRouter,
    get_dropbase_router,
)

router = APIRouter(
    prefix="/sync", tags=["sync"], responses={404: {"description": "Not found"}}
)


@router.get("/{app_name}/{page_name}")
async def get_state_context(app_name: str, page_name: str):
    return get_page_state_context(app_name, page_name)


@router.post("/columns/")
async def sync_table_columns_req(
    req: SyncTableColumns, access_cookies: AccessCookies = Depends(get_access_cookies)
):
    args = req.dict()
    args["access_cookies"] = access_cookies.dict()
    return run_process_task("sync_table_columns", args)


@router.post("/get_table_columns/")
async def get_table_columns_req(req: GetTableColumns):
    return run_process_task("get_table_columns", req.dict())


@router.post("/components/")
async def sync_components_req(
    req: SyncComponents, router: DropbaseRouter = Depends(get_dropbase_router)
):
    return sync_components(req.app_name, req.page_name, router)


@router.put("/page/{page_id}")
async def sync_page_state_req(
    page_id: str, router: DropbaseRouter = Depends(get_dropbase_router)
):
    return sync_page(page_id, router)
