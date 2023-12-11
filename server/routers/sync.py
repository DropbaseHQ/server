from fastapi import APIRouter, Depends, Response

from server.controllers.query import get_table_columns
from server.controllers.sync import (
    get_page_state_context,
    sync_components,
    sync_page,
    sync_table_columns,
)
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.schemas.sync import GetTableColumns, SyncComponents, SyncTableColumns

router = APIRouter(prefix="/sync", tags=["sync"], responses={404: {"description": "Not found"}})


@router.get("/{app_name}/{page_name}")
def get_state_context_req(app_name: str, page_name: str):
    return get_page_state_context(app_name, page_name)


@router.post("/columns/")
def sync_table_columns_req(req: SyncTableColumns, router: DropbaseRouter = Depends(get_dropbase_router)):
    return sync_table_columns(req, router)


# TODO: check with client, remove this endpoint
@router.post("/get_table_columns/")
def get_table_columns_req(req: GetTableColumns, response: Response):
    return get_table_columns(req.app_name, req.page_name, req.file, req.state)


@router.post("/components/")
def sync_components_req(req: SyncComponents, router: DropbaseRouter = Depends(get_dropbase_router)):
    return sync_components(req.app_name, req.page_name, router)


@router.put("/page/{page_id}")
def sync_page_state_req(page_id: str, router: DropbaseRouter = Depends(get_dropbase_router)):
    return sync_page(page_id, router)
