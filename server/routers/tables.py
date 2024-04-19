import json
import uuid

import anyio
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response

from dropbase.schemas.table import CommitTableColumnsRequest, ConvertTableRequest
from server.controllers.columns import commit_table_columns
from server.controllers.redis import r
from server.controllers.tables import convert_sql_table
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.utils import get_permission_dependency_array

router = APIRouter(
    prefix="/tables", tags=["tables"], responses={404: {"description": "Not found"}}
)


def convert_sql_table_sync_wrapper(req, router):
    anyio.run(convert_sql_table, req, router)


@router.post("/convert/")
async def convert_sql_table_req(
    req: ConvertTableRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    router: DropbaseRouter = Depends(get_dropbase_router),
):

    job_id = uuid.uuid4().hex
    background_tasks.add_task(convert_sql_table, req, router, job_id)

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


@router.post(
    "/commit/",
    dependencies=get_permission_dependency_array(action="edit", resource="app"),
)
def commit_table_columns_req(req: CommitTableColumnsRequest, response: Response):
    try:
        return commit_table_columns(req)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
