import asyncio
import os

from fastapi import APIRouter, HTTPException, Request

from server.controllers.workspace import WorkspaceFolderController
from server.utils import get_permission_dependency_array

router = APIRouter(prefix="/page", tags=["page"])

cwd = os.getcwd()


def get_page_permissions(action: str = "use"):
    return get_permission_dependency_array(action, "app")


def get_app_id(request: Request):
    app_name = request.path_params.get("app_name")
    if app_name is None:
        if request.headers.get("content-type") == "application/json":
            body = asyncio.run(request.json())
            return body.get("app_name")
        return None
    if app_name is None:
        raise HTTPException(status_code=400, detail="No app name provided")

    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=os.path.join(cwd, "workspace")
    )
    app_id = workspace_folder_controller.get_app_id(app_name=app_name)
    if app_id is None:
        raise HTTPException(
            status_code=400,
            detail=(f"App {app_name} either does not exist or has no id."),
        )
    return app_id
