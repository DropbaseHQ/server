import json
import uuid

from fastapi import APIRouter, HTTPException, Response

from dropbase.helpers.utils import get_table_data_fetcher
from dropbase.schemas.files import DataFile
from dropbase.schemas.function import RunFunction
from dropbase.schemas.run_python import RunPythonStringRequestNew
from server.controllers.properties import read_page_properties
from server.controllers.python_docker import run_container
from server.controllers.redis import r
from server.utils import get_permission_dependency_array

router = APIRouter(
    prefix="/function",
    tags=["function"],
    responses={404: {"description": "Not found"}},
    dependencies=get_permission_dependency_array(action="use", resource="app"),
)


# run function
@router.post("/")
async def run_function_req(req: RunFunction, response: Response):
    try:
        properties = read_page_properties(req.app_name, req.page_name)
        file = get_table_data_fetcher(properties["files"], req.file_name)

        if req.function_name:
            file["function"] = req.function_name

        if file is None:
            raise HTTPException(status_code=404, detail="Function not found")

        file = DataFile(**file)

        job_id = uuid.uuid4().hex
        env_vars = {
            "app_name": req.app_name,
            "page_name": req.page_name,
            "file": json.dumps(file.dict()),
            "state": json.dumps(req.state),
            "job_id": job_id,
            "type": "file",
        }
        # start a job
        run_container(env_vars)

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/string/")
async def run_python_string(req: RunPythonStringRequestNew, response: Response):
    try:
        job_id = uuid.uuid4().hex
        env_vars = {
            "file_code": req.file_code,
            "test_code": req.test_code,
            "app_name": req.app_name,
            "page_name": req.page_name,
            "state": json.dumps(req.state),
            "job_id": job_id,
            "type": "string",
        }
        run_container(env_vars)

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
        raise HTTPException(status_code=500, detail=str(e))
