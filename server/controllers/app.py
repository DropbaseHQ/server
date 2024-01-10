import os

from server.constants import cwd


def get_subdirectories(path):
    return [
        name
        for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name)) and name != "__pycache__"
    ]


def get_workspace_apps():
    folder_path = os.path.join(cwd, "workspace")
    app_names = get_subdirectories(folder_path)
    response = []
    for app_name in app_names:
        page_path = os.path.join(folder_path, app_name)
        page_names = get_subdirectories(page_path)
        pages = [{"name": page} for page in page_names]
        response.append({"name": app_name, "pages": pages})
    return response
