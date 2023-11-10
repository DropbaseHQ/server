from fastapi import APIRouter

from server.schemas.run_python import QueryPythonRequest
from server.worker.python_subprocess import run_process_task

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/")
async def run_query(req: QueryPythonRequest):
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "file": req.file.dict(),
        "state": req.state,
        "filter_sort": req.filter_sort.dict(),
    }
    if req.file.type == "data_fetcher":
        return run_process_task("run_python_query", args)
    else:
        return run_process_task("run_sql", args)
