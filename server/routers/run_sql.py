from fastapi import APIRouter, Response

from server.schemas.query import RunSQLRequest
from server.controllers.sql_from_srting import run_process_function
from server.controllers.query import query_db, process_query_result

router = APIRouter(prefix="/run_sql", tags=["run_sql"], responses={404: {"description": "Not found"}})


@router.post("/run_sql_string/")
async def run_sql_from_string_req(req: RunSQLRequest, response: Response):
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "file_content": req.file_content,
        "state": req.state,
    }
    resp = run_process_function("get_sql_from_file_content", args)

    if not resp["success"]:
        response.status_code = 500
        return resp
    
    filter_sql = resp["result"]["filter_sql"]
    filter_values = resp["result"]["filter_values"]
    source = req.source

    df = process_query_result(query_db(filter_sql, filter_values, source))
    resp["result"] = {"columns": df.columns.tolist(), "data": df.values.tolist()}
    return resp
