from fastapi import APIRouter, Depends

from server.schemas.query import RunSQLRequest
from server.controllers.query import run_sql_query_from_string
from server.controllers.python_subprocess import format_process_result
from server.auth.dependency import EnforceUserAppPermissions

router = APIRouter(
    prefix="/run_sql", tags=["run_sql"], responses={404: {"description": "Not found"}}
)


@router.post(
    "/run_sql_string/", dependencies=[Depends(EnforceUserAppPermissions(action="use"))]
)
async def run_sql_from_string_req(req: RunSQLRequest):
    try:
        return run_sql_query_from_string(
            req.file_content, req.source, req.app_name, req.page_name, req.state
        )
    except Exception as e:
        return format_process_result(str(e))
