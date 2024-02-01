import os

from server.constants import cwd
from server.controllers.workspace import AppFolderController, get_subdirectories


def get_workspace_apps():
    folder_path = os.path.join(cwd, "workspace")
    app_names = get_subdirectories(folder_path)
    response = []
    for app_name in app_names:
        app_folder_controller = AppFolderController(app_name, folder_path)
        pages = app_folder_controller.get_pages()
        response.append({"name": app_name, "pages": pages})
    return response
