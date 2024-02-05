import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Response

from server.auth.dependency import EnforceUserAppPermissions
from server.controllers.connect import connect_to_user_db
from server.controllers.properties import read_page_properties
from server.controllers.python_docker import run_container
from server.controllers.redis import r
from server.controllers.run_sql import run_sql_query
from server.controllers.utils import get_table_data_fetcher
from server.schemas.files import DataFile
from server.schemas.query import RunSQLRequest
from server.schemas.run_python import QueryPythonRequest, RunPythonStringRequestNew

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/sql_string/", dependencies=[Depends(EnforceUserAppPermissions(action="use"))])
async def run_sql_from_string_req(
    request: RunSQLRequest, response: Response, background_tasks: BackgroundTasks
):
    job_id = uuid.uuid4().hex
    user_db = connect_to_user_db(request.source)
    background_tasks.add_task(user_db.run_sql_query_from_string, request, job_id)

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


@router.post("/python_string/")
async def run_python_string_test(
    req: RunPythonStringRequestNew,
    response: Response,
    background_tasks: BackgroundTasks,
):
    job_id = uuid.uuid4().hex
    args = {
        "file_code": req.file_code,
        "test_code": req.test_code,
        "state": json.dumps(req.state),
        "context": json.dumps(req.context),
        "job_id": job_id,
    }
    background_tasks.add_task(run_container, args, "inside_docker_string")

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


@router.post("/")
async def start_docker(req: QueryPythonRequest, response: Response, background_tasks: BackgroundTasks):
    properties = read_page_properties(req.app_name, req.page_name)
    file = get_table_data_fetcher(properties["files"], req.table.fetcher)
    file = DataFile(**file)
    job_id = uuid.uuid4().hex
    args = {"app_name": req.app_name, "page_name": req.page_name, "job_id": job_id}
    if file.type == "data_fetcher":
        # need to turn into json to pass to docker container as environment variables
        args["file"] = json.dumps(file.dict())
        args["state"] = json.dumps(req.state)
        background_tasks.add_task(run_container, args)
    else:
        # called internally, so can pass objects directly
        args["file"] = file
        args["state"] = req.state
        args["filter_sort"] = req.filter_sort
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


@router.get("/status/{job_id}")
async def get_job_status(job_id: str, response: Response, use_cache=False):
    result_json = r.get(job_id)
    if result_json:
        result = json.loads(result_json.decode("utf-8"))
        response.status_code = result.get("status_code")
        result.pop("status_code")
        return result
    else:
        response.status_code = 404
        return {"message": "job not found"}
