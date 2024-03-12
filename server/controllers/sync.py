from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from server.controllers.workspace import WorkspaceFolderController
from server.controllers.app import AppFolderController
from server.requests.dropbase_router import DropbaseRouter
import os


cwd = os.getcwd()


def sync_with_dropbase(router: DropbaseRouter):
    # Get all workspace info, including workspace, apps, and their pages
    workspace_path = os.path.join(cwd, "workspace")
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=workspace_path
    )
    workspace_apps = workspace_folder_controller.get_workspace_properties()
    workspace_app_structure = []

    for app in workspace_apps:
        if app.get("name") is None:
            continue

        app_structure = {
            "id": app.get("id"),
            "name": app.get("name"),
        }

        app_folder_controller = AppFolderController(
            app_name=app.get("name"),
            r_path_to_workspace=workspace_path,
        )
        app_properties = app_folder_controller._get_app_properties_data()

        if not app_properties:
            workspace_app_structure.append(app_structure)
            continue

        page_info = app_properties.get("pages", [])

        app_structure["pages"] = page_info
        workspace_app_structure.append(app_structure)
    workspace_structure = {"apps": workspace_app_structure}

    structure_response = router.misc.sync_structure(workspace_structure)
    apps_without_ids = structure_response.json().get("apps_without_id")
    app_with_ids = structure_response.json().get("apps_with_id")

    properties = workspace_folder_controller.get_workspace_properties()
    for app in apps_without_ids:
        for app_properties in properties:
            if app_properties.get("name") == app.get("name"):
                app_properties["status"] = "ID_NOT_FOUND_BUT_NAME_FOUND"
                break
            app_properties["status"] = "ID_NOT_FOUND_AND_NAME_NOT_FOUND"

    for app in properties:
        if app.get("id") in app_with_ids:
            app["status"] = "SYNCED"
            continue

    workspace_folder_controller.write_workspace_properties({"apps": properties})
