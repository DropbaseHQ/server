import json
import uuid

from fastapi import APIRouter, HTTPException, Response

from dropbase.schemas.function import RunClass
from dropbase.schemas.run_python import RunPythonStringRequestNew
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
@router.post("/class")
async def run_class_req(req: RunClass, response: Response):
    try:
        job_id = uuid.uuid4().hex
        env_vars = {
            "app_name": req.app_name,
            "page_name": req.page_name,
            "action": req.action,
            "target": req.target,
            "state": json.dumps(req.state),
            "job_id": job_id,
        }

        if req.action == "update":
            env_vars["edits"] = req.edits

        print("job ID: ", job_id)
        # start a job
        run_container(env_vars)

        status_code = 202
        reponse_payload = {
            "message": "Job started",
            "status_code": status_code,
            "job_id": job_id,
        }

        # set initial status to pending
        r.set(job_id, json.dumps(reponse_payload))
        r.expire(job_id, 300)  # timeout in 5 minutes

        print("set job_id", job_id, "to pending")

        response.status_code = status_code
        reponse_payload.pop("status_code")
        return reponse_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/string/")
async def run_python_string(req: RunPythonStringRequestNew, response: Response):
    # TODO: update this to use class based method
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
