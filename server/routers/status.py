import json

from fastapi import APIRouter, Response

from server.controllers.redis import r

router = APIRouter(prefix="/status", tags=["status"], responses={404: {"description": "Not found"}})


@router.get("/{job_id}")
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
