import json
import os
import shutil
import tempfile

from fastapi import HTTPException

from dropbase.helpers.boilerplate import app_properties_boilerplate
from server.constants import cwd
from server.controllers.workspace import WorkspaceFolderController, get_subdirectories


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
        shutil.rmtree(self.app_path)

    def create_app(self):
        # TODO: handle workspace properties
        self.create_dirs()
        self.create_app_init_properties()
        self.add_app_to_workspace()
        return {"message": "success"}

    def get_pages(self):
        if os.path.exists(os.path.join(self.app_path, "properties.json")):
            return [{"name": p} for p in self._get_app_properties_data().keys()]

        page_names = get_subdirectories(self.app_path)
        pages = [{"name": page} for page in page_names]
        return pages

    def _get_app_properties_data(self):
        path_to_app_properties = os.path.join(self.app_path, "properties.json")
        if not os.path.exists(path_to_app_properties):
            return None
        with open(path_to_app_properties, "r") as file:
            return json.load(file)


def get_workspace_apps():
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

        app_controller = AppController(app.get("name"), app.get("label"))
        pages = app_controller.get_pages()
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
