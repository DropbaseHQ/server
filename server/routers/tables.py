import json
import uuid

import anyio
from fastapi import APIRouter, BackgroundTasks, Depends, Response

from dropbase.schemas.table import CommitTableColumnsRequest, ConvertTableRequest, TableBase
from server.auth.dependency import CheckUserPermissions
from server.controllers.columns import commit_table_columns
from server.controllers.python_docker import run_container
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

    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "job_id": job_id,
        "type": "smart",
    }
    args["table"] = json.dumps(req.table.dict())
    args["state"] = json.dumps(req.state)

    background_tasks.add_task(run_container, args)
    # Now correctly scheduling the wrapper function
    return {"message": "Conversion started", "job_id": job_id}


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
