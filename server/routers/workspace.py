import os

from fastapi import APIRouter, Depends

from dropbase.helpers.utils import check_if_object_exists
from server.controllers.workspace import WorkspaceFolderController

router = APIRouter(
    prefix="/worker_workspace",
    tags=["worker_workspace"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_workspace() -> dict:

    # response = router.auth.get_worker_workspace()
    # workspace_info = response.json()
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=os.path.join(os.getcwd(), "workspace")
    )
    # Adds workspace id to workspace properties if not there already
    if check_if_object_exists("workspace/properties.json"):
        workspace_props = workspace_folder_controller.get_workspace_properties()
        return workspace_props
    return None
