from fastapi import APIRouter

from server.schemas.run_python import QueryPythonRequest
from server.controllers.query import run_sql_query, run_python_query
from server.controllers.python_subprocess import format_process_result

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/")
async def run_query(req: QueryPythonRequest):
    try:
        if req.file.type == "data_fetcher":
            resp = run_python_query(req.app_name, req.page_name, req.file, req.state, req.filter_sort)
        else:
            resp = run_sql_query(req.app_name, req.page_name, req.file, req.state, req.filter_sort)
        return resp
    except Exception as e:
        return format_process_result(str(e))