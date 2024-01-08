import os

from server.constants import cwd


def get_workspace_apps():
    folder_path = os.path.join(cwd, "workspace")
    apps = [
        name
        for name in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, name)) and name != "__pycache__"
    ]
    response = []
    for app in apps:
        response.append({"name": app, "pages": [{"name": "page1"}]})
    return response
