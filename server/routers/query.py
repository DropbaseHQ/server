from fastapi import APIRouter, Response

from server.schemas.run_python import QueryPythonRequest
from server.controllers.query import query_db, process_query_result
from server.worker.python_subprocess import run_process_task

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/")
async def run_query(req: QueryPythonRequest, response: Response):
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "file_name": req.file.name,
        "state": req.state,
        "filter_sort": req.filter_sort.dict(),
    }
    if req.file.type == "data_fetcher":
        resp, status_code = run_process_task("run_python_query", args)
    else:
        resp, status_code = run_process_task("get_sql_from_file", args)
        if status_code == 200:
            filter_sql = resp["result"]["filter_sql"]
            filter_values = resp["result"]["filter_values"]
            res = query_db(filter_sql, filter_values, req.file.source)
            df = process_query_result(res)
            resp["result"] = {"columns": df.columns.tolist(), "data": df.values.tolist()}
    response.status_code = status_code
    return resp
