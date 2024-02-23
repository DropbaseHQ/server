from fastapi import APIRouter, Depends, Response

from dropbase.schemas.table import CommitTableColumnsRequest, ConvertTableRequest, GetDbTypeRequest
from server.auth.dependency import CheckUserPermissions
from server.controllers.columns import commit_table_columns
from server.controllers.tables import convert_sql_table, get_database_type_from_source
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(prefix="/tables", tags=["tables"], responses={404: {"description": "Not found"}})


@router.post("/convert/")
def convert_sql_table_req(
    req: ConvertTableRequest,
    response: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    resp, status_code = convert_sql_table(req, router)
    response.status_code = status_code
    return resp


@router.post(
    "/commit/",
    dependencies=[Depends(CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP))],
)
def commit_table_columns_req(req: CommitTableColumnsRequest, response: Response):
    try:
        return commit_table_columns(req)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.post("/get_database_type")
def get_db_type(req: GetDbTypeRequest, response: Response):
    try:
        return get_database_type_from_source(req)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}
