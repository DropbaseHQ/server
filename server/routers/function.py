import json
import uuid

from fastapi import APIRouter, HTTPException, Response

from dropbase.schemas.function import RunClass, RunPythonStringRequest
from server.constants import DEFAULT_RESPONSES, TASK_TIMEOUT
from server.controllers.python_docker import run_container
from server.helpers.redis import r

router = APIRouter(prefix="/function", tags=["function"], responses=DEFAULT_RESPONSES)


# run function
@router.post("/class/")
async def run_class_req(req: RunClass, response: Response):
    # TODO: move this to controllers
    try:
        job_id = uuid.uuid4().hex
        env_vars = {
            "app_name": req.app_name,
            "page_name": req.page_name,
            "action": req.action,
            "resource": req.resource,
            "section": req.section,
            "component": req.component if req.component else "",
            "updates": json.dumps(req.updates if req.updates else [{}]),
            "row": json.dumps(req.row if req.row else {}),
            "state": json.dumps(req.state),
            "job_id": job_id,
            "type": "class",
        }

        # start a job
        run_container(env_vars)

        status_code = 202
        reponse_payload = {"message": "Job started", "status_code": status_code, "job_id": job_id}

        # set initial status to pending
        r.set(job_id, json.dumps(reponse_payload))
        r.expire(job_id, TASK_TIMEOUT)  # timeout in 5 minutes

        response.status_code = status_code
        reponse_payload.pop("status_code")
        return reponse_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/string/")
async def run_python_string(req: RunPythonStringRequest, response: Response):
    # TODO: update this to use class based method
    try:
        job_id = uuid.uuid4().hex
        env_vars = {
            "code": req.code,
            "test": req.test,
            "state": json.dumps(req.state),
            "job_id": job_id,
            "type": "string",
        }
        run_container(env_vars)

        status_code = 202
        reponse_payload = {"message": "job started", "status_code": status_code, "job_id": job_id}

        # set initial status to pending
        r.set(job_id, json.dumps(reponse_payload))
        r.expire(job_id, TASK_TIMEOUT)  # timeout in 5 minutes

        response.status_code = status_code
        reponse_payload.pop("status_code")
        return reponse_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
