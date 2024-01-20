import copy

from server.tests.constants import TEST_APP_NAME, TEST_PAGE_NAME, WORKSPACE_PATH
from server.tests.verify_file_exists import workspace_file_exists

base_data = {
    "name": "REPLACE_ME",
    "app_name": TEST_APP_NAME,
    "page_name": TEST_PAGE_NAME,
    "type": "sql",
    "source": None,
}


def test_create_file_req(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "test_file"

    # Act
    res = test_client.post("/files/", json=data)

    # Assert
    assert res.status_code == 200
    assert workspace_file_exists("scripts/test_file.sql")


def test_create_file_req_ui(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "test_file"
    data["type"] = "ui"

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code == 200
    assert workspace_file_exists("scripts/test_file.py")


def test_create_file_req_data_fetcher(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "data_fetcher"
    data["type"] = "data_fetcher"

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code == 200
    assert workspace_file_exists("scripts/data_fetcher.py")


def test_create_file_req_bad_request(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "test_file"
    data["type"] = "bad_type"

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code != 200
    assert not workspace_file_exists("scripts/test_file.py")


def test_create_file_req_block_path_traversal_vulnerability(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "../test_file"

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code != 200
    assert not workspace_file_exists("test_file.sql")


def test_rename_file_req(test_client):
    # Arrange
    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "old_name": "test_ui",
        "new_name": "test_renamed",
        "type": "ui",
    }

    # Act
    res = test_client.put("/files/rename", json=data)

    # Assert
    assert res.status_code == 200
    assert not workspace_file_exists("scripts/test_ui.py")
    assert workspace_file_exists("scripts/test_renamed.py")


def test_rename_file_req_file_not_exists(test_client):
    # Arrange
    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "old_name": "test_uis",
        "new_name": "test_renamed",
        "type": "ui",
    }

    # Act
    res = test_client.put("/files/rename", json=data)

    # Assert
    assert res.status_code == 400
    assert workspace_file_exists("scripts/test_ui.py")
    assert not workspace_file_exists("scripts/test_renamed.py")


def test_delete_file_req(test_client):
    # Arrange
    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "file_name": "test_ui.py",
        "type": "ui",
    }

    # Act
    res = test_client.request("DELETE", "/files/", json=data)

    # Assert
    assert res.status_code == 200
    assert not workspace_file_exists("scripts/test_ui.sql")


def test_delete_file_req_platform_error(test_client):
    # Arrange
    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "file_name": "test_ui.py",
        "type": "py",
    }

    # Act
    res = test_client.request("DELETE", "/files/", json=data)

    # Assert
    assert res.status_code != 200
    assert workspace_file_exists("scripts/test_ui.py")


def test_delete_file_req_not_exists(test_client):
    # Arrange
    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "file_name": "test_uis.py",
        "type": "ui",
    }
    # Act
    res = test_client.request("DELETE", "/files/", json=data)

    # Assert
    assert res.status_code != 200


def test_update_file_req(test_client):
    # Arrange
    file_name = "test_ui"
    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "file_name": file_name,
        "code": "mock sql",
        "type": "ui",
    }

    # Act
    res = test_client.put(f"/files/{file_name}", json=data)

    # Assert
    assert res.status_code == 200

    file_path = WORKSPACE_PATH.joinpath(f"{TEST_APP_NAME}/{TEST_PAGE_NAME}/scripts/{file_name}.py")
    with open(file_path, "r") as r:
        assert r.read() == "mock sql"
