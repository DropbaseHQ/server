import os
import shutil
import sys

from fastapi import APIRouter, HTTPException

from server import requests as dropbase_router
from server.constants import DROPBASE_API_URL
from server.controllers.workspace import AppCreator
from server.schemas.workspace import CreateAppRequest, DeleteAppRequest, RenameAppRequest

cwd = os.getcwd()

router = APIRouter(prefix="/app", tags=["app"], responses={404: {"description": "Not found"}})


@router.post("/")
def create_app_req(req: CreateAppRequest):
    sys.path.insert(0, cwd)

    app_response = dropbase_router.get_app(app_id=req.app_id)
    app_object = app_response.json()
    if app_response.status_code != 200:
        raise HTTPException(status_code=404, detail="App not found")

    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_creator = AppCreator(
        app_object=app_object,
        app_template=req.app_template,
        r_path_to_workspace=r_path_to_workspace,
        dropbase_api_url=DROPBASE_API_URL,
    )
    return app_creator.create()


@router.put("/{app_id}")
def rename_app_req(app_id, req: RenameAppRequest):
    workspace_folder_path = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_path = os.path.join(workspace_folder_path, req.old_name)
    new_path = os.path.join(workspace_folder_path, req.new_name)
    if os.path.exists(app_path):
        os.rename(app_path, new_path)
    resp = dropbase_router.rename_app(rename_data={"app_id": app_id, **req.dict()})
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Unable to rename app")


@router.delete("/{app_id}")
def delete_app_req(app_id, req: DeleteAppRequest):
    app_path = os.path.join(os.path.dirname(__file__), "../../workspace", req.app_name)
    del_resp = dropbase_router.delete_app(app_id=app_id)
    if del_resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Unable to delete app")
    if os.path.exists(app_path):
        shutil.rmtree(app_path)
