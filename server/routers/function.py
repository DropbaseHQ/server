import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Response

from server.controllers.properties import read_page_properties
from server.controllers.python_docker import run_container
from server.controllers.redis import r
from server.controllers.utils import get_table_data_fetcher
from server.schemas.files import DataFile
from server.schemas.function import RunFunction

router = APIRouter(
    prefix="/function",
    tags=["function"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def run_function_req(req: RunFunction, response: Response, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex
    properties = read_page_properties(req.app_name, req.page_name)
    file = get_table_data_fetcher(properties["files"], req.function_name)
    file = DataFile(**file)

    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "file": json.dumps(file.dict()),
        "state": json.dumps(req.payload.state),
        "context": json.dumps(req.payload.context),
        "job_id": job_id,
    }
    # start a job
    background_tasks.add_task(run_container, args)

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
