from fastapi import APIRouter

from server import requests as dropbase_router
from server.controllers.utils import handle_state_context_updates
from server.schemas.workspace import ConvertTableRequest, CreateTableRequest, UpdateTableRequest
from server.worker.python_subprocess import run_process_task

router = APIRouter(prefix="/tables", tags=["tables"], responses={404: {"description": "Not found"}})


@router.post("/")
def create_table_req(req: CreateTableRequest):
    resp = dropbase_router.create_table(**req.dict())
    handle_state_context_updates(resp)
    return resp.json()


from server.worker.tables import update_table


@router.put("/{table_id}/")
def update_table_req(table_id: str, req: UpdateTableRequest):
    return update_table(table_id=table_id, req=req.dict())
    args = {"table_id": table_id, "req": req.dict()}
    return run_process_task("update_table", args)


@router.post("/convert/")
def convert_table_req(req: ConvertTableRequest):
    # TODO: move to queue
    return run_process_task("convert_table", req.dict())


@router.delete("/{table_id}/")
def delete_table_req(table_id: str):
    resp = dropbase_router.delete_table(table_id=table_id)
    handle_state_context_updates(resp)
    return resp.json()
