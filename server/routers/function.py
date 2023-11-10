from fastapi import APIRouter, Response

from server.schemas.function import RunFunction
from server.worker.python_subprocess import run_process_task

router = APIRouter(
    prefix="/function",
    tags=["function"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def run_function(req: RunFunction, resp: Response):
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "function_name": req.function_name,
        "payload": req.payload.dict(),
    }
    return run_process_task("run_python_ui", args)
