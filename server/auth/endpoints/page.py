import asyncio
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from server.utils import get_permission_dependency_array, get_permission_dependency
from server.controllers.page import get_state_context
from ..controllers import user as user_controller
from ..connect import get_db
from ..authentication import get_current_user
from ..schemas import CheckPermissionRequest
from server.controllers.workspace import WorkspaceFolderController

router = APIRouter(prefix="/page", tags=["page"])

cwd = os.getcwd()


def get_page_permissions(action: str = "use"):
    return get_permission_dependency_array(action, "app")


def get_app_id(request: Request):
    app_name = request.path_params.get("app_name")
    if app_name is None:
        if request.headers.get("content-type") == "application/json":
            body = asyncio.run(request.json())
            return body.get("app_name")
        return None
    if app_name is None:
        raise HTTPException(status_code=400, detail="No app name provided")

    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=os.path.join(cwd, "workspace")
    )
    app_id = workspace_folder_controller.get_app_id(app_name=app_name)
    if app_id is None:
        raise HTTPException(
            status_code=400,
            detail=(f"App {app_name} either does not exist or has no id."),
        )
    return app_id


@router.get("/{app_name}/{page_name}", dependencies=get_page_permissions("use"))
def get_st_cntxt(
    request: Request,
    app_name: str,
    page_name: str,
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    app_id = get_app_id(request)
    permissions = user_controller.check_permissions(
        db=db,
        user=user,
        request=CheckPermissionRequest(app_id=app_id),
        workspace_id=request.headers.get("workspace-id"),
    )
    print("permissions", permissions)
    return get_state_context(app_name, page_name, permissions.get("app_permissions"))
