from fastapi import APIRouter

from server.controllers.python import run_process_with_exec
from server.schemas.run_python import RunPythonStringRequest

router = APIRouter(
    prefix="/run_python", tags=["run_python"], responses={404: {"description": "Not found"}}
)


@router.post("/run_python_string/")
async def run_python_string(req: RunPythonStringRequest):
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "python_string": req.python_string,
        "payload": req.payload.dict(),
        "file": req.file,
    }
    return run_process_with_exec(args)
