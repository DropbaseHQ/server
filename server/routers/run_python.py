from fastapi import APIRouter, Depends

from server.controllers.python_from_string import run_process_with_exec
from server.schemas.run_python import RunPythonStringRequest
from server.auth.dependency import EnforceUserAppPermissions

router = APIRouter(
    prefix="/run_python",
    tags=["run_python"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/run_python_string/",
    dependencies=[Depends(EnforceUserAppPermissions(action="use"))],
)
async def run_python_string(req: RunPythonStringRequest):
    args = {
        "app_name": req.app_name,
        "page_name": req.page_name,
        "python_string": req.python_string,
        "payload": req.payload.dict(),
        "file": req.file,
    }
    return run_process_with_exec(args)
