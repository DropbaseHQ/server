import os

from fastapi import APIRouter, Depends

from dropbase.schemas.page import CreatePageRequest, PageProperties, RenamePageRequest
from server.controllers.page import get_state_context, update_page_properties
from server.controllers.workspace import AppFolderController
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.utils import get_permission_dependency_array

router = APIRouter(
    prefix="/page", tags=["page"], responses={404: {"description": "Not found"}}
)


def get_page_permissions(action: str = "use"):
    return get_permission_dependency_array(action, "app")


@router.get("/{app_name}/{page_name}", dependencies=get_page_permissions("use"))
def get_st_cntxt(
    app_name: str,
    page_name: str,
    permissions: dict = (
        get_page_permissions("use")[0] if get_page_permissions("use") else None
    ),
):
    return get_state_context(app_name, page_name, permissions)


@router.post("/", dependencies=get_page_permissions("edit"))
def create_page_req(
    request: CreatePageRequest, router: DropbaseRouter = Depends(get_dropbase_router)
):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(request.app_name, r_path_to_workspace)
    return app_folder_controller.create_page(
        router=router, page_name=request.page_name, page_label=request.page_label
    )


@router.put("/{app_name}/{page_name}", dependencies=get_page_permissions("edit"))
def rename_page_req(app_name: str, page_name: str, request: RenamePageRequest):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(app_name, r_path_to_workspace)
    return app_folder_controller.rename_page(
        page_name=page_name, new_page_label=request.new_page_label
    )


@router.delete("/{app_name}/{page_name}", dependencies=get_page_permissions("edit"))
def delete_page_req(
    app_name: str, page_name: str, router: DropbaseRouter = Depends(get_dropbase_router)
):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(app_name, r_path_to_workspace)
    return app_folder_controller.delete_page(page_name=page_name, router=router)


@router.put("/", dependencies=get_page_permissions("edit"))
def cud_page_props(req: PageProperties):
    return update_page_properties(req)
