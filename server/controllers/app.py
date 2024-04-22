import json
import os

from dropbase.helpers.boilerplate import app_properties_boilerplate
from server.constants import cwd
from server.controllers.workspace import AppFolderController, get_subdirectories
from server.requests.dropbase_router import DropbaseRouter


class AppController:
    def __init__(self, app_name: str, app_label: str) -> None:
        self.app_name = app_name
        self.app_label = app_label
        self.app_path = f"workspace/{self.app_name}"
        self.app = None

    def create_dirs(self):
        os.mkdir(self.app_path)

    def create_app_init_properties(self):
        # assuming page name is page1 by default
        with open(f"workspace/{self.app_name}/properties.json", "w") as f:
            f.write(json.dumps(app_properties_boilerplate, indent=2))

    def add_app_to_workspace(self):
        with open("workspace/properties.json", "r") as f:
            workspace_properties = json.loads(f.read())
        apps = workspace_properties.get("apps", [])
        app = {"name": self.app_name, "label": self.app_label}
        apps.append(app)
        workspace_properties["apps"] = apps
        with open("workspace/properties.json", "w") as file:
            file.write(json.dumps(workspace_properties, indent=2))

    def delete_app(self):
        os.rmdir(self.app_path)

    def create_app(self):
        # TODO: handle workspace properties
        self.create_dirs()
        self.create_app_init_properties()
        self.add_app_to_workspace()
        return {"message": "success"}


def get_workspace_apps(router: DropbaseRouter):
    folder_path = os.path.join(cwd, "workspace")
    apps = []
    if os.path.exists(os.path.join(folder_path, "properties.json")):
        with open(os.path.join(folder_path, "properties.json"), "r") as file:
            apps = json.load(file)["apps"]
    else:
        app_names = get_subdirectories(folder_path)
        apps = [{"name": app_name, "label": app_name, "id": None} for app_name in app_names]
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
    # return response
    return parse_apps_permissions(response, router)


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
