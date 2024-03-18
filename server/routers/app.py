import os

from fastapi import APIRouter, Depends

from dropbase.schemas.workspace import CreateAppRequest, RenameAppRequest
from server.controllers.app import get_workspace_apps
from server.controllers.workspace import AppFolderController, WorkspaceFolderController
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(
    prefix="/app", tags=["app"], responses={404: {"description": "Not found"}}
)


@router.get("/list/")
def get_user_apps(router: DropbaseRouter = Depends(get_dropbase_router)):
    return get_workspace_apps(router=router)


@router.post("/")
def create_app_req(
    req: CreateAppRequest,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(
        app_name=req.app_name, r_path_to_workspace=r_path_to_workspace
    )
    return app_folder_controller.create_app(router=router, app_label=req.app_label)


@router.put("/")
def rename_app_req(req: RenameAppRequest):
    # assert page does not exist
    path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=path_to_workspace
    )
    return workspace_folder_controller.update_app_info(
        app_id=req.app_id, new_label=req.new_label
    )


@router.delete("/{app_name}")
def delete_app_req(
    app_name: str, router: DropbaseRouter = Depends(get_dropbase_router)
):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(app_name, r_path_to_workspace)
    return app_folder_controller.delete_app(app_name=app_name, router=router)
