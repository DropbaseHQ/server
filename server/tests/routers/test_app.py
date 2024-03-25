import os
import shutil

import pytest

from server.controllers.workspace import WorkspaceFolderController
from server.tests.constants import TEST_APP_NAME, WORKSPACE_PATH

NEW_APP_LABEL = "Test create app"
NEW_APP_NAME = "test_create_app"
OLD_APP_NAME = "test_create_app_2"
TEST_WORKSPACE_ID = "test_workspace"


def check_directory_structure(path):
    # Define the paths to check
    paths_to_check = [
        os.path.join(path, "state.py"),
        os.path.join(path, "context.py"),
        os.path.join(path, "properties.json"),
        os.path.join(path, "scripts"),
    ]

    # Check if each path exists
    for path in paths_to_check:
        if not os.path.exists(path):
            return False

    return True


class MockResponse:
    status_code = 200


def test_create_app_req(test_client, dropbase_router_mocker):
    try:
        # Arrange
        data = {
            "app_label": NEW_APP_LABEL,
            "app_name": NEW_APP_NAME,
            "workspace_id": TEST_WORKSPACE_ID,
        }

        # Act
        # dropbase_router_mocker.patch(
        #     "auth",
        #     "verify_identity_token",
        #     side_effect=lambda *args, **kwargs: MockResponse(),
        # )
        dropbase_router_mocker.patch(
            "app", "create_app", side_effect=lambda *args, **kwargs: MockResponse()
        )
        dropbase_router_mocker.patch(
            "page", "create_page", side_effect=lambda *args, **kwargs: MockResponse()
        )
        headers = {"access-token": "mock access token"}
        res = test_client.post("/app/", json=data, headers=headers)

        # Assert
        assert res.status_code == 200
        assert check_directory_structure(f"workspace/{NEW_APP_NAME}/page1")
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath(NEW_APP_NAME), ignore_errors=True)


def test_create_app_req_error_duplicate_labels(test_client, dropbase_router_mocker):
    # Arrange
    data = {
        "app_label": NEW_APP_LABEL,
        "app_name": "a_different_name",
        "workspace_id": TEST_WORKSPACE_ID,
    }

    # Act
    dropbase_router_mocker.patch(
        "app", "create_app", side_effect=lambda *args, **kwargs: MockResponse()
    )
    dropbase_router_mocker.patch(
        "page", "create_page", side_effect=lambda *args, **kwargs: MockResponse()
    )
    test_client.post("/app/", json=data)

    headers = {"access-token": "mock access token"}
    res = test_client.post("/app/", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert res_data["detail"] == "Another app with the same label already exists"


def test_create_app_req_error_duplicate_names(test_client, dropbase_router_mocker):
    # Arrange
    data = {
        "app_label": "a_different_label",
        "app_name": NEW_APP_NAME,
        "workspace_id": TEST_WORKSPACE_ID,
    }

    # Act
    dropbase_router_mocker.patch(
        "app", "create_app", side_effect=lambda *args, **kwargs: None
    )
    test_client.post("/app/", json=data)
    headers = {"access-token": "mock access token"}
    res = test_client.post("/app/", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert res_data["detail"] == "Another app with the same name already exists"


def test_create_app_req_error_illegal_name_space_between(
    test_client, dropbase_router_mocker
):
    # Arrange
    data = {
        "app_label": NEW_APP_LABEL,
        "app_name": "My New App",
        "workspace_id": TEST_WORKSPACE_ID,
    }

    # Act
    dropbase_router_mocker.patch(
        "app", "create_app", side_effect=lambda *args, **kwargs: None
    )
    headers = {"access-token": "mock access token"}
    res = test_client.post("/app/", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not check_directory_structure("workspace/My New App/page1")

    assert (
        res_data["detail"]
        == "Invalid app name. Only alphanumeric characters and underscores are allowed"
    )


def test_create_app_req_error_illegal_name_special_characters(
    test_client, dropbase_router_mocker
):
    # Arrange
    data = {
        "app_label": NEW_APP_LABEL,
        "app_name": "My_New_App!",
        "workspace_id": TEST_WORKSPACE_ID,
    }

    # Act
    dropbase_router_mocker.patch(
        "app", "create_app", side_effect=lambda *args, **kwargs: None
    )
    headers = {"access-token": "mock access token"}
    res = test_client.post("/app/", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not check_directory_structure("workspace/My_New_App/page1")

    assert (
        res_data["detail"]
        == "Invalid app name. Only alphanumeric characters and underscores are allowed"
    )


def test_create_app_req_error_illegal_name_url_path(
    test_client, dropbase_router_mocker
):
    # Arrange
    data = {
        "app_label": NEW_APP_LABEL,
        "app_name": "../../my_app",
        "workspace_id": TEST_WORKSPACE_ID,
    }

    # Act
    dropbase_router_mocker.patch(
        "app", "create_app", side_effect=lambda *args, **kwargs: None
    )
    headers = {"access-token": "mock access token"}
    res = test_client.post("/app/", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not check_directory_structure("workspace/../../my_app/page1")

    assert (
        res_data["detail"]
        == "Invalid app name. Only alphanumeric characters and underscores are allowed"
    )


@pytest.mark.skip(
    reason="Rename endpoint no longer renames app_name, only label. Label is not used in the file system."
)
def test_rename_app_req_error_duplicate_names(test_client, dropbase_router_mocker):
    # Arrange
    data = {"app_name": NEW_APP_NAME, "workspace_id": TEST_WORKSPACE_ID}
    create_app = test_client.post("/app/", json=data)

    # Act
    req = {
        "old_name": OLD_APP_NAME,
        "new_name": NEW_APP_NAME,
        "app_id": "23ea28dc-4e2d-4d48-b15e-09b51f1a1c74",
    }

    dropbase_router_mocker.patch(
        "app", "create_app", side_effect=lambda *args, **kwargs: None
    )
    res = test_client.put("/app/", json=req)
    res_data = res.json()

    # Assert
    assert create_app.status_code == 200
    assert res.status_code != 200

    assert res_data["message"] == "An app with this name already exists"


def test_rename_app_req(test_client):
    try:
        # Arrange
        workspace_folder_controller = WorkspaceFolderController(
            r_path_to_workspace=WORKSPACE_PATH
        )
        app_id = workspace_folder_controller.get_app_id(app_name=TEST_APP_NAME)
        data = {"app_id": app_id, "new_label": NEW_APP_NAME}

        # Act
        headers = {"access-token": "mock access token"}
        res = test_client.put("/app/", json=data, headers=headers)

        workspace_props = workspace_folder_controller.get_workspace_properties()
        apps = workspace_props.get("apps", [])
        app_still_has_old_name = False
        app_has_new_label = False
        for app in apps:
            if app.get("id") == app_id:
                app_still_has_old_name = app.get("name") == TEST_APP_NAME
                app_has_new_label = app.get("label") == NEW_APP_NAME

        # Assert
        assert res.status_code == 200
        assert check_directory_structure(f"workspace/{TEST_APP_NAME}/page1")
        assert app_still_has_old_name
        assert app_has_new_label
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath(NEW_APP_NAME), ignore_errors=True)


def test_delete_app_req(test_client, dropbase_router_mocker):
    # Act

    dropbase_router_mocker.patch(
        "app", "delete_app", side_effect=lambda *args, **kwargs: MockResponse()
    )
    headers = {"access-token": "mock access token"}
    res = test_client.request("DELETE", f"/app/{TEST_APP_NAME}", headers=headers)

    # Assert
    assert res.status_code == 200
    assert not check_directory_structure(f"workspace/{TEST_APP_NAME}/page1")


def test_delete_app_req_block_path_traversal_attack(test_client):
    # Arrange
    try:
        test_target_path = WORKSPACE_PATH.parent.joinpath(
            "test_delete_app_req_block_path_traversal_attack_folder"
        )
        test_target_rel_path = (
            "../test_delete_app_req_block_path_traversal_attack_folder"
        )
        os.mkdir(test_target_path)

        # Act
        headers = {"access-token": "mock access token"}
        res = test_client.request(
            "DELETE", f"/app/{test_target_rel_path}", headers=headers
        )

        # Assert
        assert res.status_code != 200
        assert os.path.exists(test_target_path)
    finally:
        shutil.rmtree(test_target_path)
