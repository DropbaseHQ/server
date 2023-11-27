from fastapi import APIRouter

from server.schemas.query import RunSQLRequest
from server.controllers.sql_from_srting import run_process_function

router = APIRouter(prefix="/run_sql", tags=["run_sql"], responses={404: {"description": "Not found"}})


@router.post("/run_sql_string/")
async def run_sql_from_string_req(req: RunSQLRequest):
    return run_process_function("run_sql_from_string", req.dict())
