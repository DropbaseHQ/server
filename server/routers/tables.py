from fastapi import APIRouter, Response, Depends
from server.controllers.utils import handle_state_context_updates
from server.schemas.workspace import (
    ConvertTableRequest,
    CreateTableRequest,
    UpdateTableRequest,
)
from server.worker.python_subprocess import run_process_task
from server.requests.dropbase_router import (
    DropbaseRouter,
    get_dropbase_router,
    AccessCookies,
    get_access_cookies,
)
from server.worker.tables import update_table, update_table_columns

router = APIRouter(
    prefix="/tables", tags=["tables"], responses={404: {"description": "Not found"}}
)


@router.post("/")
def create_table_req(
    req: CreateTableRequest, router: DropbaseRouter = Depends(get_dropbase_router)
):
    resp = router.table.create_table(**req.dict())
    handle_state_context_updates(resp)
    return resp.json()


@router.put("/{table_id}/")
def update_table_req(
    table_id: str,
    response: Response,
    req: UpdateTableRequest,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    # TODO: sync this flow with client
    resp, status_code = update_table(table_id, req, router)
    if status_code != 200:
        response.status_code = status_code
        return resp
    if req.file.get("id") != req.table.get("file_id"):
        resp, status_code = update_table_columns(table_id, req, router)
        response.status_code = status_code
        return resp
    return resp.json()


@router.post("/convert/")
def convert_table_req(
    req: ConvertTableRequest,
    response: Response,
    access_cookies: AccessCookies = Depends(get_access_cookies),
):
    args = req.dict()
    args["access_cookies"] = access_cookies.dict()
    resp, status_code = run_process_task("convert_table", args)
    response.status_code = status_code
    return resp


@router.delete("/{table_id}/")
def delete_table_req(
    table_id: str, router: DropbaseRouter = Depends(get_dropbase_router)
):
    resp = router.table.delete_table(table_id=table_id)
    handle_state_context_updates(resp)
    return resp.json()
