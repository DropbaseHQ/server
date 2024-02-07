from fastapi import APIRouter, Response

from dropbase.schemas.edit_cell import EditCellRequest
from server.controllers.edit_cell import edit_cell

router = APIRouter(prefix="/edit_cell", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/edit_sql_table/")
async def edit_sql_table_req(req: EditCellRequest, response: Response):
    resp, status_code = edit_cell(req.file, req.edits)

    response.status_code = status_code
    return resp
