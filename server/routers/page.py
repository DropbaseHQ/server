import os

from fastapi import APIRouter

from dropbase.schemas.page import CreatePageRequest, PageProperties, RenamePageRequest
from server.controllers.page import get_state_context, update_page_properties
from server.controllers.workspace import AppFolderController

router = APIRouter(
    prefix="/page", tags=["page"], responses={404: {"description": "Not found"}}
)


@router.get("/{app_name}/{page_name}/init")
def get_init_st_cntxt(app_name: str, page_name: str):
    return get_state_context(app_name, page_name, initial=True)


@router.get("/{app_name}/{page_name}")
def get_st_cntxt(app_name: str, page_name: str):
    return get_state_context(app_name, page_name)


@router.post("/")
def create_page_req(request: CreatePageRequest):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(request.app_name, r_path_to_workspace)
    return app_folder_controller.create_page(
        page_name=request.page_name, page_label=request.page_label
    )


@router.put("/{app_name}/{page_name}")
def rename_page_req(app_name: str, page_name: str, request: RenamePageRequest):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(app_name, r_path_to_workspace)
    return app_folder_controller.rename_page(
        page_name=page_name, new_page_label=request.new_page_label
    )


@router.delete("/{app_name}/{page_name}")
def delete_page_req(app_name: str, page_name: str):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(app_name, r_path_to_workspace)
    return app_folder_controller.delete_page(page_name=page_name)


@router.put("/")
def cud_page_props(req: PageProperties):
    return update_page_properties(req)
