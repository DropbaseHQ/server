from fastapi import APIRouter, Depends, Response

from server.controllers.columns import commit_table_columns
from server.controllers.tables import convert_sql_table
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.schemas.workspace import CommitTableColumnsRequest, ConvertTableRequest

router = APIRouter(prefix="/tables", tags=["tables"], responses={404: {"description": "Not found"}})


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


@router.post("/commit/")
def commit_table_columns_req(
    req: CommitTableColumnsRequest,
    response: Response,
):
    try:
        return commit_table_columns(req)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}
