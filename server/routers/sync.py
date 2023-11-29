from fastapi import APIRouter, Depends, Response
from server.schemas.sync import SyncComponents, SyncTableColumns
from server.worker.sync import sync_components, sync_page
from server.controllers.sync import sync_table_columns, get_page_state_context
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router


router = APIRouter(
    prefix="/sync", tags=["sync"], responses={404: {"description": "Not found"}}
)


@router.get("/{app_name}/{page_name}")
async def get_state_context_req(app_name: str, page_name: str):
    return get_page_state_context(app_name, page_name)


@router.post("/columns/")
async def sync_table_columns_req(
    req: SyncTableColumns,
    response: Response,
    router: DropbaseRouter = Depends(get_dropbase_router)
):
    resp, status_code = sync_table_columns(
        req.app_name,
        req.page_name,
        req.table,
        req.file,
        req.state,
        router
    )
    response.status_code = status_code
    return resp


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
