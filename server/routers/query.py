import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Response

from dropbase.helpers.utils import get_table_data_fetcher
from dropbase.schemas.files import DataFile
from dropbase.schemas.query import (
    RunSQLRequestTask,
    RunSQLStringRequest,
    RunSQLStringTask,
)
from dropbase.schemas.run_python import QueryPythonRequest
from dropbase.schemas.table import FilterSort
from server.controllers.properties import read_page_properties
from server.controllers.redis import r
from server.controllers.run_sql import run_sql_query, run_sql_query_from_string

router = APIRouter(
    prefix="/query", tags=["query"], responses={404: {"description": "Not found"}}
)


@router.post("/")
async def run_sql(
    req: QueryPythonRequest, response: Response, background_tasks: BackgroundTasks
):
    try:
        properties = read_page_properties(req.app_name, req.page_name)
        file = get_table_data_fetcher(properties["files"], req.fetcher)
        file = DataFile(**file)
        job_id = uuid.uuid4().hex
        filter_sort = (
            req.filter_sort if req.filter_sort else FilterSort(filters=[], sorts=[])
        )

        # called internally, so can pass objects directly
        args = RunSQLRequestTask(
            app_name=req.app_name,
            page_name=req.page_name,
            table_name=req.table_name,
            file=file,
            filter_sort=filter_sort,
            state=req.state,
            job_id=job_id,
        )
        background_tasks.add_task(run_sql_query, args)

        status_code = 202
        reponse_payload = {
            "message": "job started",
            "status_code": status_code,
            "job_id": job_id,
        }

        # set initial status to pending
        r.set(job_id, json.dumps(reponse_payload))
        r.expire(job_id, 300)  # timeout in 5 minutes

        response.status_code = status_code
        reponse_payload.pop("status_code")
        return reponse_payload
    except Exception as e:
        response.status_code = 500
        return {"message": str(e)}


@router.post("/string/")
async def run_sql_from_string(
    request: RunSQLStringRequest, response: Response, background_tasks: BackgroundTasks
):
    job_id = uuid.uuid4().hex
    args = RunSQLStringTask(**request.dict(), job_id=job_id)
    background_tasks.add_task(run_sql_query_from_string, args)

    status_code = 202
    reponse_payload = {
        "message": "job started",
        "status_code": status_code,
        "job_id": job_id,
    }

    # set initial status to pending
    r.set(job_id, json.dumps(reponse_payload))
    r.expire(job_id, 300)  # timeout in 5 minutes

    response.status_code = status_code
    reponse_payload.pop("status_code")
    return reponse_payload
