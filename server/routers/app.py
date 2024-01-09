import os
import shutil
import sys

from fastapi import APIRouter, Depends

from server.controllers.app import get_workspace_apps
from server.controllers.workspace import AppCreator
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.schemas.workspace import CreateAppRequest, DeleteAppRequest, RenameAppRequest

cwd = os.getcwd()

router = APIRouter(prefix="/app", tags=["app"], responses={404: {"description": "Not found"}})


@router.get("/list/")
def get_user_apps():
    return get_workspace_apps()


@router.post("/")
def create_app_req(req: CreateAppRequest):

    sys.path.insert(0, cwd)  # TODO: check if we need this line

    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_creator = AppCreator(
        app_name=req.app_name,
        r_path_to_workspace=r_path_to_workspace,
    )
    return app_creator.create()


@router.put("/{app_id}")
def rename_app_req(app_id, req: RenameAppRequest, router: DropbaseRouter = Depends(get_dropbase_router)):
    workspace_folder_path = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_path = os.path.join(workspace_folder_path, req.old_name)
    new_path = os.path.join(workspace_folder_path, req.new_name)
    if os.path.exists(app_path):
        os.rename(app_path, new_path)
    return {"success": True}


@router.delete("/{app_id}")
def delete_app_req(app_id, req: DeleteAppRequest, router: DropbaseRouter = Depends(get_dropbase_router)):
    app_path = os.path.join(os.path.dirname(__file__), "../../workspace", req.app_name)
    if os.path.exists(app_path):
        shutil.rmtree(app_path)
    return {"success": True}
