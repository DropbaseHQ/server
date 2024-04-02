import json
import uuid

import anyio
from fastapi import APIRouter, BackgroundTasks, Depends, Response

from dropbase.schemas.table import CommitTableColumnsRequest, ConvertTableRequest
from server.auth.dependency import CheckUserPermissions
from server.controllers.columns import commit_table_columns
from server.controllers.redis import r
from server.controllers.tables import convert_sql_table
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(prefix="/tables", tags=["tables"], responses={404: {"description": "Not found"}})


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
    dependencies=[Depends(CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP))],
)
def commit_table_columns_req(req: CommitTableColumnsRequest, response: Response):
    try:
        return commit_table_columns(req)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}
