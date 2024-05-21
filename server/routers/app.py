from fastapi import APIRouter

from dropbase.schemas.workspace import CreateAppRequest, RenameAppRequest
from server.controllers.app import AppController, get_workspace_apps
from server.controllers.page_controller import PageController

router = APIRouter(prefix="/app", tags=["app"], responses={404: {"description": "Not found"}})


@router.post("/")
def create_app_req(request: CreateAppRequest):
    appController = AppController(request.app_name)
    appController.create_app(request.app_label)
    pageController = PageController(request.app_name, "page1")
    pageController.create_page("Page 1")
    return {"message": "success"}


@router.put("/")
def rename_app_req(request: RenameAppRequest):
    appController = AppController(request.app_name)
    appController.rename(request.new_label)
    return {"message": "success"}


@router.delete("/{app_name}")
def delete_app_req(app_name: str):
    appController = AppController(app_name)
    appController.delete_app()
    return {"message": "App deleted successfully"}


@router.get("/list/")
def get_user_apps():
    return get_workspace_apps()
