from fastapi import APIRouter

from server.schemas.edit_cell import EditCellRequest
from server.worker.python_subprocess import run_process_task

router = APIRouter(prefix="/edit_cell", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/edit_sql_table/")
async def edit_sql_table_req(req: EditCellRequest):
    edits = [edit.dict() for edit in req.edits]
    args = {"file": req.file, "edits": edits}
    return run_process_task("edit_cell", args)
