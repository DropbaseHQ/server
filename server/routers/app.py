import os

from fastapi import APIRouter, Depends, Response

from dropbase.schemas.workspace import CreateAppRequest, RenameAppRequest
from server.controllers.app import get_workspace_apps
from server.controllers.utils import check_if_object_exists, validate_column_name
from server.controllers.workspace import AppFolderController, WorkspaceFolderController
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(prefix="/app", tags=["app"], responses={404: {"description": "Not found"}})


@router.get("/list/")
def get_user_apps():
    return get_workspace_apps()


@router.post("/")
def create_app_req(
    req: CreateAppRequest,
    response: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    if not validate_column_name(req.app_name):
        response.status_code = 400
        return {"message": "Invalid app name. Only alphanumeric characters and underscores are allowed"}

    # assert page does not exist
    if check_if_object_exists(f"workspace/{req.app_name}/"):
        response.status_code = 400
        return {"message": "An app with this name already exists"}

    try:
        r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
        app_folder_controller = AppFolderController(
            app_name=req.app_name, r_path_to_workspace=r_path_to_workspace
        )
        return app_folder_controller.create_app(workspace_id=req.workspace_id, router=router)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.put("/")
def rename_app_req(req: RenameAppRequest, response: Response):
    # assert page does not exist
    path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    workspace_folder_controller = WorkspaceFolderController(r_path_to_workspace=path_to_workspace)

    target_app = workspace_folder_controller.get_app(app_id=req.app_id)
    if target_app is None:
        response.status_code = 400
        return {"message": "App does not exist, or id does not exist for this app."}

    workspace_folder_controller.update_app_info(
        app_id=req.app_id, app_info={**target_app, "label": req.new_label}
    )

    # if check_if_object_exists(f"workspace/{req.new_name}/"):
    #     response.status_code = 400
    #     return {"message": "An app with this name already exists"}

    # workspace_folder_path = os.path.join(os.path.dirname(__file__), "../../workspace")
    # app_path = os.path.join(workspace_folder_path, req.old_name)
    # new_path = os.path.join(workspace_folder_path, req.new_name)
    # if os.path.exists(app_path):
    #     os.rename(app_path, new_path)
    return {"success": True}


@router.delete("/{app_name}")
def delete_app_req(
    app_name: str,
    response: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(app_name, r_path_to_workspace)
    return app_folder_controller.delete_app(app_name=app_name, response=response, router=router)
