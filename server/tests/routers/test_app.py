import os
import shutil

from server.tests.constants import WORKSPACE_PATH
from server.tests.mocks.dropbase.app import (
    delete_app_response,
    delete_app_response_path_traversal,
    get_app_response,
    rename_app_response,
    update_app_response,
)
from server.tests.mocks.dropbase.sync import sync_components_response_empty
from server.tests.mocks.util import mock_response
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_app_req(test_client, dropbase_router_mocker):
    try:
        # Arrange
        dropbase_router_mocker.patch(
            "misc", "sync_components", side_effect=sync_components_response_empty
        )
        dropbase_router_mocker.patch(
            "app", "get_app", side_effect=get_app_response(name="test_create_app")
        )
        dropbase_router_mocker.patch("app", "update_app", side_effect=update_app_response)

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
        shutil.rmtree(WORKSPACE_PATH.joinpath("test_create_app"), ignore_errors=True)


def test_create_app_req_error_file_creation(test_client, dropbase_router_mocker, mocker):
    try:
        # Arrange
        mocker.patch(
            "server.controllers.workspace.create_file", side_effect=Exception("mock file creation error")
        )
        dropbase_router_mocker.patch(
            "misc", "sync_components", side_effect=sync_components_response_empty
        )
        dropbase_router_mocker.patch(
            "app", "get_app", side_effect=get_app_response(name="test_create_app")
        )
        dropbase_router_mocker.patch("app", "update_app", side_effect=update_app_response)

        data = {"app_id": "123456123456", "app_template": {"page": {"name": "page1"}}}

        # Act
        res = test_client.post("/app", json=data)

        # Assert
        assert res.status_code != 200
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath("test_create_app"), ignore_errors=True)


def test_create_app_req_platform_error_update_app(test_client, dropbase_router_mocker):
    try:
        # Arrange
        dropbase_router_mocker.patch(
            "misc", "sync_components", side_effect=sync_components_response_empty
        )
        dropbase_router_mocker.patch(
            "app", "get_app", side_effect=get_app_response(name="test_create_app")
        )
        dropbase_router_mocker.patch(
            "app",
            "update_app",
            side_effect=lambda *args, **kwargs: mock_response(json={}, status_code=500),
        )

        data = {"app_id": "123456123456", "app_template": {"page": {"name": "page1"}}}

        # Act
        res = test_client.post("/app", json=data)

        # Assert
        assert res.status_code != 200
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath("test_create_app"), ignore_errors=True)


def test_create_app_req_platform_error_get_app(test_client, dropbase_router_mocker):
    try:
        # Arrange
        dropbase_router_mocker.patch(
            "misc", "sync_components", side_effect=sync_components_response_empty
        )
        dropbase_router_mocker.patch(
            "app", "get_app", side_effect=lambda *args, **kwargs: mock_response(json={}, status_code=500)
        )
        dropbase_router_mocker.patch("app", "update_app", side_effect=update_app_response)

        data = {"app_id": "123456123456", "app_template": {"page": {"name": "page1"}}}

        # Act
        res = test_client.post("/app", json=data)

        # Assert
        assert res.status_code != 200
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath("test_create_app"), ignore_errors=True)


def test_create_app_req_platform_error_sync_components(test_client, dropbase_router_mocker):
    try:
        # Arrange
        dropbase_router_mocker.patch(
            "misc",
            "sync_components",
            side_effect=lambda *args, **kwargs: mock_response(json={}, status_code=500),
        )
        dropbase_router_mocker.patch(
            "app", "get_app", side_effect=get_app_response(name="test_create_app")
        )
        dropbase_router_mocker.patch("app", "update_app", side_effect=update_app_response)

        data = {"app_id": "123456123456", "app_template": {"page": {"name": "page1"}}}

        # Act
        res = test_client.post("/app", json=data)

        # Assert
        assert res.status_code != 200
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath("test_create_app"), ignore_errors=True)


def test_rename_app_req(test_client, dropbase_router_mocker):
    try:
        # Arrange
        dropbase_router_mocker.patch("app", "rename_app", side_effect=rename_app_response)

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


def test_delete_app_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("app", "delete_app", side_effect=delete_app_response)

    data = {"app_name": "dropbase_test_app"}

    # Act
    res = test_client.request("DELETE", "/app/bf5a519f-b9df-4f09-9f10-ce2f18d9a5ca", json=data)

    # Assert
    assert res.status_code == 200
    assert not os.path.exists(WORKSPACE_PATH.joinpath("dropbase_test_app"))


def test_delete_app_req_block_path_traversal_attack(test_client, dropbase_router_mocker):
    # Arrange
    try:
        test_target_path = WORKSPACE_PATH.parent.joinpath(
            "test_delete_app_req_block_path_traversal_attack_folder"
        )
        test_target_rel_path = "../test_delete_app_req_block_path_traversal_attack_folder"
        os.mkdir(test_target_path)

        dropbase_router_mocker.patch(
            "app", "delete_app", side_effect=delete_app_response_path_traversal(test_target_rel_path)
        )

        data = {"app_name": str(test_target_rel_path)}

        # Act
        res = test_client.request("DELETE", "/app/bf5a519f-b9df-4f09-9f10-ce2f18d9a5ca", json=data)

        # Assert
        assert res.status_code != 200
        assert os.path.exists(test_target_path)
    finally:
        shutil.rmtree(test_target_path)
