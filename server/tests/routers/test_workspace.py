import os
import shutil

from server.tests.constants import WORKSPACE_PATH
from server.tests.mocks.dropbase.app import (
    get_app_response,
    update_app_response,
    delete_app_response,
    rename_app_response,
)
from server.tests.mocks.dropbase.sync import sync_components_response_empty
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_app_req(test_client, mocker):
    try:
        # Arrange
        mocker.patch("server.requests.sync_components", side_effect=sync_components_response_empty)
        mocker.patch("server.requests.get_app", side_effect=get_app_response(name="test_create_app"))
        mocker.patch("server.requests.update_app", side_effect=update_app_response)

        data = {"app_id": "123456123456", "app_template": {"page": {"name": "page1"}}}

        # Act
        res = test_client.post("/app", json=data)

        # Assert
        assert res.status_code == 200
        assert is_valid_folder_structure(app="test_create_app")
        assert workspace_object_exists("State", "widgets", app="test_create_app")
        assert workspace_object_exists("State", "tables", app="test_create_app")
        assert workspace_object_exists("Context", "widgets", app="test_create_app")
        assert workspace_object_exists("Context", "tables", app="test_create_app")
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath("test_create_app"))


def test_rename_app_req(test_client, mocker):
    try:
        # Arrange
        mocker.patch("server.requests.rename_app", side_effect=rename_app_response)

        data = {
            "old_name": "dropbase_test_app",
            "new_name": "dropbase_test_app_renamed",
        }

        # Act
        res = test_client.put("/app/bf5a519f-b9df-4f09-9f10-ce2f18d9a5ca", json=data)

        # Assert
        assert res.status_code == 200
        assert not os.path.exists(WORKSPACE_PATH.joinpath("dropbase_test_app"))
        assert os.path.exists(WORKSPACE_PATH.joinpath("dropbase_test_app_renamed"))
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath("dropbase_test_app_renamed"))


def test_delete_app_req(test_client, mocker):
    # Arrange
    mocker.patch("server.requests.delete_app", side_effect=delete_app_response)

    data = {"app_name": "dropbase_test_app"}

    # Act
    res = test_client.request("DELETE", "/app/bf5a519f-b9df-4f09-9f10-ce2f18d9a5ca", json=data)

    # Assert
    assert res.status_code == 200
    assert not os.path.exists(WORKSPACE_PATH.joinpath("dropbase_test_app"))
