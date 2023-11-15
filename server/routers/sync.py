from fastapi import APIRouter, Response, Depends

from server.schemas.sync import GetTableColumns, SyncComponents, SyncTableColumns
from server.worker.python_subprocess import run_process_task
from server.worker.sync import sync_components
from server.requests.dropbase_router import get_access_cookies, AccessCookies

router = APIRouter(
    prefix="/sync", tags=["sync"], responses={404: {"description": "Not found"}}
)


@router.post("/columns/")
async def sync_table_columns_req(
    req: SyncTableColumns,
    resp: Response,
    access_cookies: AccessCookies = Depends(get_access_cookies),
):
    args = req.dict()
    args["access_cookies"] = access_cookies.dict()
    return run_process_task("sync_table_columns", args)


@router.post("/get_table_columns/")
async def get_table_columns_req(req: GetTableColumns, resp: Response):
    return run_process_task("get_table_columns", req.dict())


@router.post("/components/")
async def sync_components_req(
    req: SyncComponents,
    resp: Response,
    access_cookies: AccessCookies = Depends(get_access_cookies),
):
    return sync_components(req.app_name, req.page_name, access_cookies)
