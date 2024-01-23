from fastapi import APIRouter, Response

from server.controllers.page import (
    create_page,
    delete_page,
    get_page_state_context,
    rename_page,
    update_page_properties,
)
from server.controllers.properties import read_page_properties
from server.controllers.utils import check_if_object_exists, validate_column_name
from server.schemas.page import CreatePageRequest, PageProperties, RenamePageRequest

router = APIRouter(prefix="/page", tags=["page"], responses={404: {"description": "Not found"}})


@router.get("/{app_name}/{page_name}")
def get_state_context_req(app_name: str, page_name: str, response: Response):
    try:
        state_context = get_page_state_context(app_name, page_name)
        state_context["properties"] = read_page_properties(app_name, page_name)
        return state_context
    except Exception as e:
        response.status_code = 400
        return {"message": str(e)}


@router.post("/{app_name}")
def create_page_req(
    app_name: str,
    request: CreatePageRequest,
    response: Response,
):
    try:
        # assert app_name is valid
        if not validate_column_name(request.page_name):
            response.status_code = 400
            return {
                "message": "Invalid page name. Only alphanumeric characters and underscores are allowed"
            }

        # assert page does not exist
        if check_if_object_exists(f"workspace/{app_name}/{request.page_name}/"):
            response.status_code = 400
            return {"message": "Page already exists"}

        return create_page(app_name, request.page_name)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.put("/{app_name}/{page_name}")
def rename_page_req(
    app_name: str,
    page_name: str,
    request: RenamePageRequest,
    response: Response,
):
    try:
        return rename_page(app_name, page_name, request.new_page_name)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.delete("/{app_name}/{page_name}")
def delete_page_req(
    app_name: str,
    page_name: str,
    response: Response,
):
    try:
        return delete_page(app_name, page_name)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.post("/")
def cud_page_props(
    req: PageProperties,
    response: Response,
):
    try:
        # update local json file
        return update_page_properties(req)
    except Exception as e:
        # TODO: delete files if error
        response.status_code = 500
        return {"message": str(e)}
