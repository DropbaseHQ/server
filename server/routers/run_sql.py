from fastapi import APIRouter

from server.schemas.query import RunSQLRequest
from server.controllers.query import run_sql_query_from_string

router = APIRouter(prefix="/run_sql", tags=["run_sql"], responses={404: {"description": "Not found"}})


@router.post("/run_sql_string/")
async def run_sql_from_string_req(req: RunSQLRequest):
    return run_sql_query_from_string(req.file_content, req.source, req.app_name, req.page_name, req.state)
