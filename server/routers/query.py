import json
import uuid

import sqlalchemy.exc
from fastapi import APIRouter, BackgroundTasks, HTTPException, Response

from server.controllers.properties import read_page_properties
from server.controllers.python_docker import run_container
from server.controllers.python_from_string import run_python_script_from_string
from server.controllers.python_subprocess import format_process_result, run_process_task_unwrap
from server.controllers.run_sql import run_sql_query, run_sql_query_from_string
from server.controllers.utils import get_table_data_fetcher
from server.schemas.files import DataFile
from server.schemas.query import RunSQLRequest
from server.schemas.run_python import (
    QueryPythonRequest,
    RunPythonStringRequest,
    RunPythonStringRequestNew,
)

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


@router.post("/test_python_string/")
async def run_python_string_test(req: RunPythonStringRequestNew, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex
    args = {
        "file_code": req.file_code,
        "test_code": req.test_code,
        "state": json.dumps(req.state),
        "context": json.dumps(req.context),
        "job_id": job_id,
    }
    background_tasks.add_task(run_container, args, "inside_docker_string")
    return {"message": "job has been scheduled", "job_id": job_id}


@router.post("/test")
async def start_docker(req: QueryPythonRequest, background_tasks: BackgroundTasks):
    properties = read_page_properties(req.app_name, req.page_name)
    file = get_table_data_fetcher(properties["files"], req.table.fetcher)
    file = DataFile(**file)
    job_id = uuid.uuid4().hex
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "file": json.dumps(file.dict()),
        "state": json.dumps(req.state),
        "job_id": job_id,
    }
    background_tasks.add_task(run_container, args)
    return {"message": "job has been scheduled", "job_id": job_id}


@router.get("/status/{job_id}")
async def get_job_status(job_id):
    import redis

    r = redis.Redis(host="localhost", port=6379, db=0)
    result_json = r.get(job_id)
    return {"message": result_json.decode("utf-8")}


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
            }
            return run_process_task_unwrap("run_python_query", args)
        else:
            resp = run_sql_query(req.app_name, req.page_name, file, req.state, req.filter_sort)
        return resp
    except sqlalchemy.exc.ProgrammingError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))
