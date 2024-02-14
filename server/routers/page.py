from fastapi import APIRouter, Depends, HTTPException, Response

from dropbase.schemas.page import CreatePageRequest, PageProperties, RenamePageRequest
from server.auth.dependency import CheckUserPermissions
from server.controllers.page import (
    create_page,
    delete_page,
    get_page_state_context,
    rename_page,
    update_page_properties,
)
from server.controllers.properties import read_page_properties
from server.controllers.utils import check_if_object_exists, validate_column_name
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(
    prefix="/page", tags=["page"], responses={404: {"description": "Not found"}}
)


@router.get(
    "/{app_name}/{page_name}",
    dependencies=[
        Depends(CheckUserPermissions(action="use", resource=CheckUserPermissions.APP))
    ],
)
def get_state_context_req(
    app_name: str,
    page_name: str,
    response: Response,
    permissions: dict = Depends(get_permissions),
):
    try:
        state_context = get_page_state_context(app_name, page_name)
        state_context["properties"] = read_page_properties(app_name, page_name)
        return {"state_context": state_context, "permissions": permissions}
    except Exception as e:
        response.status_code = 400
        return {"message": str(e)}


@router.post(
    "/{app_name}",
    dependencies=[
        Depends(CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP))
    ],
)
def create_page_req(
    app_name: str,
    request: CreatePageRequest,
    response: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
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

        return create_page(app_name, request.page_name, router)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.put(
    "/{app_name}/{page_name}",
    dependencies=[
        Depends(CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP))
    ],
)
def rename_page_req(
    app_name: str,
    page_name: str,
    request: RenamePageRequest,
    response: Response,
):
    try:
        return rename_page(
            app_name=app_name,
            page_name=page_name,
            new_page_label=request.new_page_label,
        )
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.delete(
    "/{app_name}/{page_name}",
    dependencies=[
        Depends(CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP))
    ],
)
def delete_page_req(
    app_name: str,
    page_name: str,
    response: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    try:
        return delete_page(app_name, page_name, router)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}


@router.post(
    "/",
    dependencies=[
        Depends(CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP))
    ],
)
def cud_page_props(req: PageProperties, response: Response):
    try:
        # update local json file
        return update_page_properties(req)
    except HTTPException as e:
        response.status_code = e.status_code
        return {"message": str(e.detail)}

    except Exception as e:
        # TODO: delete files if error
        response.status_code = 500
        return {"message": str(e)}
