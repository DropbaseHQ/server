import os

from server.tests.constants import WORKSPACE_PATH


def workspace_file_exists(path: str, app: str = "dropbase_test_app", page: str = "page1") -> bool:
    app_path = WORKSPACE_PATH.joinpath(app)
    page_path = app_path.joinpath(page)
    return os.path.exists(page_path.joinpath(path))
