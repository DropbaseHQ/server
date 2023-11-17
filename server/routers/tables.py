from fastapi import APIRouter, Response

from server import requests as dropbase_router
from server.controllers.utils import handle_state_context_updates
from server.schemas.workspace import ConvertTableRequest, CreateTableRequest, UpdateTableRequest
from server.worker.python_subprocess import run_process_task
from server.worker.tables import update_table, update_table_columns

router = APIRouter(prefix="/tables", tags=["tables"], responses={404: {"description": "Not found"}})


@router.post("/")
def create_table_req(req: CreateTableRequest):
    resp = dropbase_router.create_table(**req.dict())
    handle_state_context_updates(resp)
    return resp.json()


@router.put("/{table_id}/")
def update_table_req(table_id: str, response: Response, req: UpdateTableRequest):
    # TODO: sync this flow with client
    resp = update_table(table_id, req)
    if resp.status_code != 200:
        response.status_code = resp.status_code
        return resp.text
    if req.file.get("id") != req.table.get("file_id"):
        resp = update_table_columns(table_id, req)
        return resp
    return resp.json()


@router.post("/convert/")
def convert_table_req(req: ConvertTableRequest):
    # TODO: move to queue
    return run_process_task("convert_table", req.dict())


@router.delete("/{table_id}/")
def delete_table_req(table_id: str):
    resp = dropbase_router.delete_table(table_id=table_id)
    handle_state_context_updates(resp)
    return resp.json()
