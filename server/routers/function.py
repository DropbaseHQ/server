import uuid

from fastapi import APIRouter, BackgroundTasks, Response

# from server.controllers.python_subprocess import run_process_task
from server.controllers.run_python import run_python_ui
from server.schemas.function import RunFunction

router = APIRouter(
    prefix="/function",
    tags=["function"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def run_function_req(req: RunFunction, response: Response, background_tasks: BackgroundTasks):
    """
    response:
    {
        result.context
        result.message
    }
    status_code
    """
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "function_name": req.function_name,
        "payload": req.payload.dict(),
    }
    job_id = uuid.uuid4().hex
    background_tasks.add_task(run_python_ui, args, job_id)
    # resp, status_code = run_process_task("run_python_ui", args)
    pass
    # response.status_code = status_code
    # return resp
