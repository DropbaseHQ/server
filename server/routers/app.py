import os

from fastapi import APIRouter

from dropbase.schemas.workspace import CreateAppRequest, RenameAppRequest
from server.controllers.app import AppController, get_workspace_apps
from server.controllers.page_controller import PageController
from server.controllers.workspace import WorkspaceFolderController
from server.utils import get_permission_dependency_array

router = APIRouter(prefix="/app", tags=["app"], responses={404: {"description": "Not found"}})


@router.post("/", dependencies=get_permission_dependency_array("edit", "workspace"))
def create_app_req(request: CreateAppRequest):
    appController = AppController(request.app_name, request.app_label)
    appController.create_app()
    pageController = PageController(request.app_name, "page1")
    pageController.create_page("Page 1")
    return {"message": "success"}


@router.put("/", dependencies=get_permission_dependency_array("edit", "workspace"))
def rename_app_req(req: RenameAppRequest):
    # assert page does not exist
    path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    workspace_folder_controller = WorkspaceFolderController(r_path_to_workspace=path_to_workspace)
    return workspace_folder_controller.update_app_info(app_id=req.app_id, new_label=req.new_label)


@router.delete("/{app_name}", dependencies=get_permission_dependency_array("edit", "workspace"))
def delete_app_req(app_name: str):
    appController = AppController(app_name, "")
    appController.delete_app()
    return {"message": "App deleted successfully"}


@router.get("/list/", dependencies=get_permission_dependency_array("use", "workspace"))
def get_user_apps():
    return get_workspace_apps().get("apps")
