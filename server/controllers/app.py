import json
import os

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
                "status": app.get("status"),
                "pages": pages,
            }
        )
    return response
    # return parse_apps_permissions(response, router)


def parse_apps_permissions(app_list, router: DropbaseRouter):

    app_ids = [app.get("id") for app in app_list]
    permissions_response = router.auth.check_apps_permissions(app_ids=app_ids).json()

    filtered_apps = []
    for app in app_list:
        if app.get("id") is None:
            filtered_apps.append(app)

        if app.get("id") in permissions_response:
            if not permissions_response.get(app.get("id")):
                continue
            filtered_apps.append(app)

    return filtered_apps
