import os
import json

from server.constants import cwd
from server.controllers.workspace import AppFolderController, get_subdirectories
from server.requests.dropbase_router import DropbaseRouter


def get_workspace_apps(router: DropbaseRouter):
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
                "pages": pages,
            }
        )
    filtered_apps = []
    permissions_response = router.auth.check_apps_permissions(
        app_ids=[app.get("id") for app in response]
    ).json()

    for app in response:
        if app.get("id") in permissions_response:
            if not permissions_response.get(app.get("id")):
                continue
            filtered_apps.append(app)

    return filtered_apps
