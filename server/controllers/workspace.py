import json
import os


class WorkspaceFolderController:
    def write_workspace_properties(self, workspace_properties: dict):
        with open("workspace/properties.json", "w") as file:
            json.dump(workspace_properties, file, indent=2)

    def read_workspace_properties(self):
        with open("workspace/properties.json", "r") as file:
            return json.load(file)


def get_subdirectories(path):
    return [
        name
        for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name)) and name != "__pycache__"
    ]
