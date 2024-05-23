from fastapi import APIRouter, HTTPException

from dropbase.schemas.workspace import CreateAppRequest, RenameAppRequest
from server.constants import DEFAULT_RESPONSES
from server.controllers.app import AppController, get_workspace_apps
from server.controllers.page_controller import PageController

router = APIRouter(prefix="/app", tags=["app"], responses=DEFAULT_RESPONSES)


@router.post("/")
def create_app_req(request: CreateAppRequest):
    try:
        appController = AppController(request.app_name)
        appController.create_app(request.app_label)
        pageController = PageController(request.app_name, "page1")
        pageController.create_page("Page 1")
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/")
def rename_app_req(request: RenameAppRequest):
    try:
        appController = AppController(request.app_name)
        appController.rename(request.new_label)
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{app_name}")
def delete_app_req(app_name: str):
    try:
        appController = AppController(app_name)
        appController.delete_app()
        return {"message": "App deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list/")
def get_user_apps():
    try:
        return get_workspace_apps()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
