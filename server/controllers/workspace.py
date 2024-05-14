import json
import os

from fastapi import HTTPException


class WorkspaceFolderController:
    def __init__(self, r_path_to_workspace: str):
        self.r_path_to_workspace = r_path_to_workspace

    def write_workspace_properties(self, workspace_properties: dict):
        workspace_properties_path = os.path.join(self.r_path_to_workspace, "properties.json")
        with open(workspace_properties_path, "w") as file:
            json.dump(workspace_properties, file, indent=2)

    def get_workspace_properties(self):
        if os.path.exists(os.path.join(self.r_path_to_workspace, "properties.json")):
            with open(os.path.join(self.r_path_to_workspace, "properties.json"), "r") as file:

                props = json.load(file)
                return props

        return None

    def get_app(self, app_id: str):
        workspace_props = self.get_workspace_properties()
        workspace_data = workspace_props.get("apps", [])

        for app in workspace_data:
            if app.get("id") == app_id:
                return app
        return None

    def get_app_id(self, app_name: str):
        workspace_props = self.get_workspace_properties()
        workspace_data = workspace_props.get("apps", [])

        app_id = None
        for app in workspace_data:
            if app.get("name") == app_name:
                app_id = app.get("id", None)
                return app_id

    def update_app_info(self, app_id: str, new_label: str):
        target_app = self.get_app(app_id=app_id)
        if target_app is None:
            raise HTTPException(
                status_code=400,
                detail="App does not exist, or id does not exist for this app.",
            )
        workspace_props = self.get_workspace_properties()
        workspace_apps = workspace_props.get("apps", [])
        existing_app_labels = [a["label"] for a in workspace_apps]

        if new_label in existing_app_labels:
            raise HTTPException(status_code=400, detail="Another app with the same label already exists")

        app_info = {**target_app, "label": new_label}
        workspace_props = self.get_workspace_properties()
        workspace_data = workspace_props.get("apps", [])
        for app in workspace_data:
            if app.get("id") == app_id:
                app.update(app_info)
                break
        self.write_workspace_properties({**workspace_props, "apps": workspace_data})


def get_subdirectories(path):
    return [
        name
        for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name)) and name != "__pycache__"
    ]
