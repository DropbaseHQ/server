import sqlalchemy.exc
from fastapi import APIRouter, HTTPException, Response

from server.controllers.properties import read_page_properties
from server.controllers.python_from_string import run_python_script_from_string
from server.controllers.python_subprocess import format_process_result, run_process_task_unwrap
from server.controllers.run_sql import run_sql_query, run_sql_query_from_string
from server.controllers.utils import get_table_data_fetcher
from server.schemas.files import DataFile
from server.schemas.query import RunSQLRequest
from server.schemas.run_python import QueryPythonRequest, RunPythonStringRequest

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/sql_string/")
async def run_sql_from_string_req(request: RunSQLRequest, response: Response):
    try:
        return run_sql_query_from_string(request)
    except Exception as e:
        response.status_code = 400
        return format_process_result(str(e))


@router.post("/python_string/")
async def run_python_string(request: RunPythonStringRequest, response: Response):
    try:
        return run_python_script_from_string(request)
    except Exception as e:
        response.status_code = 400
        return format_process_result(str(e))


@router.post("/")
async def run_query_req(req: QueryPythonRequest):
    try:
        # read page properties
        properties = read_page_properties(req.app_name, req.page_name)
        file = get_table_data_fetcher(properties["files"], req.table.fetcher)
        file = DataFile(**file)

        if file.type == "data_fetcher":

            args = {
                "app_name": req.app_name,
                "page_name": req.page_name,
                "file": file.dict(),
                "state": req.state,
                "filter_sort": req.filter_sort.dict(),
            }
            return run_process_task_unwrap("run_python_query", args)
        else:
            resp = run_sql_query(req.app_name, req.page_name, file, req.state, req.filter_sort)
        return resp
    except sqlalchemy.exc.ProgrammingError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))
