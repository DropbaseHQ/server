from fastapi import APIRouter

from server.schemas.query import RunSQLRequest
from server.worker.python_subprocess import run_process_task

router = APIRouter(prefix="/run_sql", tags=["run_sql"], responses={404: {"description": "Not found"}})


@router.post("/run_sql_string/")
async def run_sql(req: RunSQLRequest):
    return run_process_task("run_sql_from_string", req.dict())
