import json
import os
import shutil

from server.controllers.workspace import get_subdirectories
from server.helpers.boilerplate import app_properties_boilerplate


class AppController:
    def __init__(self, app_name: str) -> None:
        self.app_name = app_name
        self.app_path = f"workspace/{self.app_name}"
        self.app = None

    def create_dirs(self):
        os.mkdir(self.app_path)

    def create_app_init_properties(self):
        # assuming page name is page1 by default
        with open(f"workspace/{self.app_name}/properties.json", "w") as f:
            f.write(json.dumps(app_properties_boilerplate, indent=2))

    def delete_app(self):
        shutil.rmtree(self.app_path)
        # delete from workspace properties
        with open("workspace/properties.json", "r") as f:
            workspace_properties = json.loads(f.read())
        apps = workspace_properties.get("apps", {})
        apps.pop(self.app_name)
        workspace_properties["apps"] = apps
        with open("workspace/properties.json", "w") as file:
            file.write(json.dumps(workspace_properties, indent=2))

    def create_app(self, app_label: str):

        # TODO: handle workspace properties
        if self._check_app_exists():
            raise Exception("App with such name already exists")
        if self._check_label_exists(app_label):
            raise Exception("Label already exists")
        # check if app already exists
        self.create_dirs()
        self.create_app_init_properties()
        self.add_app_to_workspace(app_label)
        return {"message": "success"}

    def add_app_to_workspace(self, app_label: str):
        with open("workspace/properties.json", "r") as f:
            workspace_properties = json.loads(f.read())
        apps = workspace_properties.get("apps", {})
        apps[self.app_name] = {"label": app_label}
        workspace_properties["apps"] = apps
        with open("workspace/properties.json", "w") as file:
            file.write(json.dumps(workspace_properties, indent=2))

    def rename(self, new_label: str):
        if self._check_label_exists(new_label):
            raise Exception("Label already exists")
        with open("workspace/properties.json", "r") as f:
            workspace_properties = json.loads(f.read())
        apps = workspace_properties.get("apps", {})
        apps[self.app_name]["label"] = new_label
        workspace_properties["apps"] = apps
        with open("workspace/properties.json", "w") as file:
            file.write(json.dumps(workspace_properties, indent=2))

    def _check_app_exists(self):
        if os.path.exists(self.app_path):
            return True
        # check in workspace properties
        with open("workspace/properties.json", "r") as f:
            workspace_properties = json.loads(f.read())
        apps = workspace_properties.get("apps", {})
        if self.app_name in apps.keys():
            return True

    def _check_label_exists(self, label):
        with open("workspace/properties.json", "r") as f:
            workspace_properties = json.loads(f.read())
        apps = workspace_properties.get("apps", {})
        for app in apps.values():
            if app["label"] == label:
                return True
        return False

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
    # TODO: confirm apps exist
    app_response = []
    with open("workspace/properties.json", "r") as f:
        workspace_properties = json.loads(f.read())
    apps = workspace_properties.get("apps", {})
    for app_name, app in apps.items():
        with open(f"workspace/{app_name}/properties.json", "r") as f:
            app_properties = json.loads(f.read())
        app_response.append(
            {
                "name": app_name,
                "label": app.get("label"),
                "pages": [{"name": p, "label": v.get("label")} for p, v in app_properties.items()],
            }
        )
    return app_response
