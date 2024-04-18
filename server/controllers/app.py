import json
import os

from server.constants import cwd
from server.controllers.workspace import (
    AppFolderController,
    get_subdirectories,
    WorkspaceFolderController,
)
from server.requests.dropbase_router import DropbaseRouter


def get_workspace_apps():
    folder_path = os.path.join(cwd, "workspace")
    apps = []
    if os.path.exists(os.path.join(folder_path, "properties.json")):
        with open(os.path.join(folder_path, "properties.json"), "r") as file:
            apps = json.load(file)["apps"]
    else:
        app_names = get_subdirectories(folder_path)
        apps = [
            {"name": app_name, "label": app_name, "id": None} for app_name in app_names
        ]
    response = []
    for app in apps:
        if not app.get("name"):
            continue
        if not os.path.exists(os.path.join(folder_path, app.get("name"))):
            continue

        app_folder_controller = AppFolderController(app.get("name"), folder_path)
        pages = app_folder_controller.get_pages()
        response.append(
            {
                "name": app.get("name"),
                "label": app.get("label"),
                "id": app.get("id"),
                "status": app.get("status"),
                "pages": pages,
            }
        )
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=os.path.join(cwd, "workspace")
    )
    workspace_props = workspace_folder_controller.get_workspace_properties()
    return {"apps": response, "workspace_id": workspace_props.get("id")}

    # return parse_apps_permissions(response, router)
