from fastapi import APIRouter

from dropbase.schemas.page import CreatePageRequest, PageProperties, SaveTableColumns
from server.controllers.page import get_page
from server.controllers.page_controller import PageController
from server.utils import get_permission_dependency_array

def_responses = {404: {"description": "Not found"}}

router = APIRouter(prefix="/page", tags=["page"], responses=def_responses)


def get_page_permissions(action: str = "use"):
    return get_permission_dependency_array(action, "app")


@router.get("/{app_name}/{page_name}/init", dependencies=get_page_permissions("use"))
def get_page_init_req(app_name: str, page_name: str):
    return get_page(app_name, page_name, initial=True)


@router.get("/{app_name}/{page_name}", dependencies=get_page_permissions("use"))
def get_page_req(app_name: str, page_name: str):
    return get_page(app_name, page_name)


@router.post("/", dependencies=get_page_permissions("edit"))
def create_page_req(request: CreatePageRequest):
    pageController = PageController(request.app_name, request.page_name)
    pageController.create_page(request.page_label)
    return {"message": "success"}


@router.put("/", dependencies=get_page_permissions("edit"))
def update_page_req(request: PageProperties):
    pageController = PageController(request.app_name, request.page_name)
    pageController.update_page_properties(request.properties)
    return {"message": "success"}


@router.put("/rename/", dependencies=get_page_permissions("edit"))
def rename_page_req(request: CreatePageRequest):
    pageController = PageController(request.app_name, request.page_name)
    pageController.update_page_to_app_properties(request.page_label)
    return {"message": "success"}


@router.delete("/{app_name}/{page_name}", dependencies=get_page_permissions("edit"))
def delete_page_req(app_name: str, page_name: str):
    pageController = PageController(app_name, page_name)
    pageController.delete_page()
    return {"message": "success"}


@router.post("/save_table_columns/", dependencies=get_page_permissions("edit"))
def save_table_columns_req(request: SaveTableColumns):
    pageController = PageController(request.app_name, request.page_name)
    pageController.save_table_columns(request.table_name, request.columns)
    return {"message": "success"}
