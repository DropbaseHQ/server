from fastapi import APIRouter, Response

from server.schemas.run_python import QueryPythonRequest
from server.worker.python_subprocess import run_process_task

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/")
async def run_query(req: QueryPythonRequest, response: Response):
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "file": req.file.dict(),
        "state": req.state,
        "filter_sort": req.filter_sort.dict(),
    }
    func_name = "run_python_query" if req.file.type == "data_fetcher" else "run_sql_query"
    resp, status_code = run_process_task(func_name, args)
    response.status_code = status_code
    return resp
