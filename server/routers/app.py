import os

from fastapi import APIRouter, Depends, HTTPException

from dropbase.schemas.workspace import (
    CreateAppRequest,
    RenameAppRequest,
    SyncAppRequest,
)
from server.controllers.app import get_workspace_apps
from server.controllers.workspace import AppFolderController, WorkspaceFolderController
from server.utils import get_permission_dependency_array

router = APIRouter(
    prefix="/app", tags=["app"], responses={404: {"description": "Not found"}}
)


@router.get("/list/", dependencies=get_permission_dependency_array("use", "workspace"))
def get_user_apps():
    return get_workspace_apps().get("apps")


@router.post("/", dependencies=get_permission_dependency_array("edit", "workspace"))
def create_app_req(
    req: CreateAppRequest,
):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(
        app_name=req.app_name, r_path_to_workspace=r_path_to_workspace
    )
    return app_folder_controller.create_app(app_label=req.app_label)


@router.put("/", dependencies=get_permission_dependency_array("edit", "app"))
def rename_app_req(req: RenameAppRequest):
    # assert page does not exist
    path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=path_to_workspace
    )
    return workspace_folder_controller.update_app_info(
        app_id=req.app_id, new_label=req.new_label
    )


@router.delete(
    "/{app_name}", dependencies=get_permission_dependency_array("edit", "app")
)
def delete_app_req(app_name: str):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(app_name, r_path_to_workspace)
    return app_folder_controller.delete_app(app_name=app_name)
