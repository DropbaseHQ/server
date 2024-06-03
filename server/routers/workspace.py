import os
from pathlib import Path

from fastapi import APIRouter

from server.constants import DEFAULT_RESPONSES
from server.controllers.workspace import WorkspaceFolderController

router = APIRouter(prefix="/worker_workspace", tags=["worker_workspace"], responses=DEFAULT_RESPONSES)


@router.get("/")
async def get_workspace() -> dict:
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=os.path.join(os.getcwd(), "workspace")
    )
    # Adds workspace id to workspace properties if not there already
    if Path("workspace/properties.json").exists()():
        workspace_props = workspace_folder_controller.get_workspace_properties()
        return workspace_props
    return None
