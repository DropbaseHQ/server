from fastapi import APIRouter, Response

from server.controllers.python_subprocess import run_process_task
from server.schemas.edit_cell import EditCellRequest

router = APIRouter(prefix="/edit_cell", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/edit_sql_table/")
async def edit_sql_table_req(req: EditCellRequest, response: Response):
    edits = [edit.dict() for edit in req.edits]
    args = {"file": req.file, "edits": edits}
    resp, status_code = run_process_task("edit_cell", args)
    response.status_code = status_code
    return resp
