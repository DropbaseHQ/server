from fastapi import APIRouter, Depends, Response

from server.controllers.tables import convert_sql_table, update_table, update_table_columns
from server.controllers.utils import handle_state_context_updates, update_state_context_files
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.schemas.workspace import ConvertTableRequest, CreateTableRequest, UpdateTableRequest

router = APIRouter(prefix="/tables", tags=["tables"], responses={404: {"description": "Not found"}})


@router.post("/")
def create_table_req(
    req: CreateTableRequest, response: Response, router: DropbaseRouter = Depends(get_dropbase_router)
):
    resp = router.table.create_table(req.dict())

    if resp.status_code != 200:
        response.status_code = resp.status_code
        return resp.text

    resp = resp.json()
    state_context = resp.get("state_context")
    update_state_context_files(**state_context)
    return resp.get("table")


@router.put("/{table_id}/")
def update_table_req(
    table_id: str,
    response: Response,
    req: UpdateTableRequest,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    # TODO: sync this flow with client
    update_resp, status_code = update_table(table_id, req, router)
    if status_code != 200:
        response.status_code = status_code
        return update_resp
    if req.file:
        if req.file.get("id") != req.table.get("file_id"):
            update_cols_result, status_code = update_table_columns(table_id, req, router)
            if status_code != 200:
                # response.status_code = status_code
                return update_resp
            update_resp = {"state_context": update_cols_result}
    update_state_context_files(**update_resp.get("state_context"))
    return update_resp.get("table")


@router.post("/convert/")
def convert_sql_table_req(
    req: ConvertTableRequest,
    response: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    resp, status_code = convert_sql_table(
        req.app_name, req.page_name, req.table, req.file, req.state, router
    )
    response.status_code = status_code
    return resp


@router.delete("/{table_id}/")
def delete_table_req(table_id: str, router: DropbaseRouter = Depends(get_dropbase_router)):
    resp = router.table.delete_table(table_id=table_id)
    handle_state_context_updates(resp)
    return resp.json()
