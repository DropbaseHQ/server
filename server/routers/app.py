import os

from fastapi import APIRouter, Depends, HTTPException

from dropbase.schemas.workspace import (
    CreateAppRequest,
    RenameAppRequest,
    SyncAppRequest,
)
from server.controllers.app import get_workspace_apps
from server.controllers.workspace import AppFolderController, WorkspaceFolderController
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.utils import get_permission_dependency_array

router = APIRouter(
    prefix="/app", tags=["app"], responses={404: {"description": "Not found"}}
)


@router.post("/sync_app", dependencies=get_permission_dependency_array("edit", "app"))
def sync_app_req(
    request: SyncAppRequest,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    try:
        path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
        workspace_folder_controller = WorkspaceFolderController(
            r_path_to_workspace=path_to_workspace
        )
        workspace_props = workspace_folder_controller.get_workspace_properties()
        workspace_apps = workspace_props.get("apps", [])
        target_app = None
        for app in workspace_apps:
            if app.get("name") == request.app_name:
                target_app = app
                break
        if (
            target_app.get("status", None) is None
            or target_app.get("status") == "SYNCED"
        ):
            return {"message": "App is already synced"}

        app_folder_controller = AppFolderController(
            app_name=request.app_name, r_path_to_workspace=path_to_workspace
        )

        app_properties = app_folder_controller._get_app_properties_data()
        app_pages = None
        if app_properties is not None:
            app_pages = app_properties.get("pages")

        sync_response = router.misc.sync_app(
            payload={
                "app_name": request.app_name,
                "app_label": target_app.get("label"),
                "generate_new": request.generate_new,
                "pages": app_pages,
            }
        )
        workspace_props = workspace_folder_controller.get_workspace_properties()
        workspace_apps = workspace_props.get("apps", [])

        response_pages = sync_response.json().get("pages")

        for app in workspace_apps:
            if app.get("name") == request.app_name:
                app["id"] = sync_response.json().get("app_id")
                app["status"] = "SYNCED"

                app_properties = app_folder_controller._get_app_properties_data()
                if response_pages is not None and len(response_pages) > 0:
                    combined_page_info = zip(
                        app_properties.get("pages"), response_pages
                    )
                    for local_page, remote_page in combined_page_info:
                        local_page["id"] = remote_page.get("id")
                        local_page["status"] = "SYNCED"

                break

        workspace_folder_controller.write_workspace_properties(
            {**workspace_props, "apps": workspace_apps}
        )
        return {"message": "App synced"}
    except Exception as e:
        print("e", e)
        raise HTTPException(status_code=500, detail="Unable to sync app with Dropbase")


@router.get("/list/", dependencies=get_permission_dependency_array("use", "workspace"))
def get_user_apps():
    return get_workspace_apps().get("apps")


@router.post("/", dependencies=get_permission_dependency_array("edit", "workspace"))
def create_app_req(
    req: CreateAppRequest,
):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(
        app_name=req.app_name, r_path_to_workspace=r_path_to_workspace
    )
    return app_folder_controller.create_app(app_label=req.app_label)


@router.put("/", dependencies=get_permission_dependency_array("edit", "app"))
def rename_app_req(req: RenameAppRequest):
    # assert page does not exist
    path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=path_to_workspace
    )
    return workspace_folder_controller.update_app_info(
        app_id=req.app_id, new_label=req.new_label
    )


@router.delete(
    "/{app_name}", dependencies=get_permission_dependency_array("edit", "app")
)
def delete_app_req(
    app_name: str, router: DropbaseRouter = Depends(get_dropbase_router)
):
    r_path_to_workspace = os.path.join(os.path.dirname(__file__), "../../workspace")
    app_folder_controller = AppFolderController(app_name, r_path_to_workspace)
    return app_folder_controller.delete_app(app_name=app_name, router=router)
