import shutil
import tempfile

import pytest
from fastapi.testclient import TestClient

from server.main import app
from server.tests.constants import *


@pytest.fixture(autouse=True)
def test_workspace():
    with tempfile.TemporaryDirectory() as workspace_backup_path:
        shutil.copytree(WORKSPACE_PATH, workspace_backup_path, dirs_exist_ok=True)
        yield
        shutil.rmtree(WORKSPACE_PATH)
        shutil.copytree(workspace_backup_path, WORKSPACE_PATH)


@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)


def pytest_sessionstart():
    from unittest.mock import patch

    from server.controllers.workspace import AppCreator, create_file
    from server.tests.mocks.dropbase.app import get_app_response, update_app_response
    from server.tests.mocks.dropbase.misc import sync_components_response_empty

    with patch("server.requests.sync_components", side_effect=sync_components_response_empty):
        with patch("server.requests.update_app", side_effect=update_app_response):
            AppCreator(
                get_app_response()("random-uuid").json(),
                {"page": {"name": "page1"}},
                WORKSPACE_PATH,
                "",
            ).create()

    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts")
    create_file(scripts_path, "", "function1.py")
    create_file(
        scripts_path,
        'from workspace.dropbase_test_app.page1 import State, Context\ndef test_function(state: State, context: Context) -> Context:\n    print("test")\n    return context',
        "test_function.py",
    )
    create_file(scripts_path, "select 1;", "test_sql.sql")


def pytest_sessionfinish():
    import shutil

    shutil.rmtree(WORKSPACE_PATH.joinpath("dropbase_test_app"))
