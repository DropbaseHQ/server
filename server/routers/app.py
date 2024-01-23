import os
import shutil

from fastapi import APIRouter, Response

from server.controllers.app import get_workspace_apps
from server.controllers.utils import check_if_object_exists, validate_column_name
from server.controllers.workspace import AppCreator
from server.schemas.workspace import CreateAppRequest, RenameAppRequest

router = APIRouter(prefix="/app", tags=["app"], responses={404: {"description": "Not found"}})


@router.get("/list/")
def get_user_apps():
    return get_workspace_apps()


@router.post("/")
def create_app_req(req: CreateAppRequest, response: Response):

    # TODO: turn this into a utility function
    if not validate_column_name(req.app_name):
        response.status_code = 400
        return {"message": "Invalid app name. Only alphanumeric characters and underscores are allowed"}

    # assert page does not exist
    if check_if_object_exists(f"workspace/{req.app_name}/"):
        response.status_code = 400
        return {"message": "An app with this name already exists"}

    try:
        r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
        app_creator = AppCreator(
            app_name=req.app_name,
            r_path_to_workspace=r_path_to_workspace,
        )
        return app_creator.create()
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.put("/")
def rename_app_req(req: RenameAppRequest):
    workspace_folder_path = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_path = os.path.join(workspace_folder_path, req.old_name)
    new_path = os.path.join(workspace_folder_path, req.new_name)
    if os.path.exists(app_path):
        os.rename(app_path, new_path)
    return {"success": True}


@router.delete("/{app_name}")
def delete_app_req(app_name: str, response: Response):
    app_path = os.path.join(os.path.dirname(__file__), "../../workspace", app_name)
    if os.path.exists(app_path):
        shutil.rmtree(app_path)
        return {"message": "App deleted"}
    else:
        response.status_code = 400
        return {"message": "App does not exist"}
