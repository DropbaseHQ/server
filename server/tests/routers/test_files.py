import copy

from server.tests.constants import TEST_APP_NAME, TEST_PAGE_NAME, WORKSPACE_PATH
from server.tests.verify_file_exists import workspace_file_exists
from server.tests.verify_property_exists import verify_property_exists
from server.tests.verify_state_and_context import verify_object_in_state_context

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
    data["name"] = "test_file_ui"
    data["type"] = "ui"

    # Act
    res = test_client.post("/files/", json=data)

    # Assert
    assert res.status_code == 200
    assert workspace_file_exists("scripts/test_file_ui.py")


def test_create_file_req_data_fetcher(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "data_fetcher"
    data["type"] = "data_fetcher"

    # Act
    res = test_client.post("/files/", json=data)

    # Assert
    assert res.status_code == 200
    assert workspace_file_exists("scripts/data_fetcher.py")


def test_create_file_req_bad_request(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "test_file"
    data["type"] = "bad_type"

    # Act
    res = test_client.post("/files/", json=data)

    # Assert
    assert res.status_code != 200
    assert not workspace_file_exists("scripts/test_file.py")


def test_create_file_req_error_duplicate_names(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "test_file"
    data["type"] = "data_fetcher"

    # Act
    if workspace_file_exists("scripts/test_file"):
        res = test_client.post("/files/", json=data)
    else:
        test_client.post("/files/", json=data)
        res = test_client.post("/files/", json=data)

    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert res_data["detail"] == "File with the same name already exists"


def test_create_file_req_error_illegal_name_space_between(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "test file"
    data["type"] = "data_fetcher"

    # Act
    res = test_client.post("/files/", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not workspace_file_exists("scripts/test file.py")

    assert res_data["detail"][0]["msg"] == 'string does not match regex "^[A-Za-z0-9_.]+$"'


def test_create_file_req_error_illegal_name_special_characters(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "test_file$"
    data["type"] = "data_fetcher"

    # Act
    res = test_client.post("/files/", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not workspace_file_exists("scripts/test file.py")

    assert res_data["detail"][0]["msg"] == 'string does not match regex "^[A-Za-z0-9_.]+$"'


def test_create_file_req_block_path_traversal_vulnerability(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["name"] = "../test_file"

    # Act
    res = test_client.post("/files/", json=data)

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
        "old_name": "test_ui_not_exists",
        "new_name": "test_renamed_not_exists",
        "type": "ui",
    }

    # Act
    res = test_client.put("/files/rename", json=data)

    # Assert
    assert res.status_code == 400
    assert not workspace_file_exists("scripts/test_ui_not_exists.py")
    assert not workspace_file_exists("scripts/test_renamed_not_exists.py")


def test_delete_file_req(test_client):
    # Arrange
    if not workspace_file_exists("scripts/test_file.sql"):
        data = copy.deepcopy(base_data)
        data["name"] = "test_file"

        test_client.post("/files/", json=data)

    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "file_name": "test_file",
        "type": "sql",
    }

    # Act
    res = test_client.request("DELETE", "/files/", json=data)

    # Assert
    assert res.status_code == 200
    assert not workspace_file_exists("scripts/test_ui.sql")


def test_delete_file_req_platform_error(test_client):
    # Arrange
    if not workspace_file_exists("scripts/test_file.sql"):
        data = copy.deepcopy(base_data)
        data["name"] = "test_file"

        test_client.post("/files/", json=data)

    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "file_name": "test_file.sql",
        "type": "sql",
    }

    # Act
    res = test_client.request("DELETE", "/files/", json=data)

    # Assert
    assert res.status_code != 200
    assert workspace_file_exists("scripts/test_file.sql")


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
    if not workspace_file_exists("scripts/test_fetcher.sql"):
        data = copy.deepcopy(base_data)
        data["name"] = "test_fetcher"

        test_client.post("/files/", json=data)

    file_name = "test_fetcher"
    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "file_name": file_name,
        "code": "mock sql",
        "type": "sql",
    }

    # Act
    res = test_client.put(f"/files/{file_name}", json=data)

    # Assert
    assert res.status_code == 200

    file_path = WORKSPACE_PATH.joinpath(f"{TEST_APP_NAME}/{TEST_PAGE_NAME}/scripts/{file_name}.sql")
    with open(file_path, "r") as r:
        assert r.read() == "mock sql"


def test_delete_binded_fetcher(test_client):
    # Arrange
    if not workspace_file_exists("scripts/test_fetcher.sql"):
        data = copy.deepcopy(base_data)
        data["name"] = "test_fetcher"

        test_client.post("/files/", json=data)

        assert workspace_file_exists("scripts/test_fetcher.sql")

    if not verify_object_in_state_context("TablesState", "table2"):
        data = {
            "app_name": TEST_APP_NAME,
            "page_name": TEST_PAGE_NAME,
            "properties": {
                "tables": [
                    {
                        "label": "Table2",
                        "name": "table2",
                        "description": None,
                        "fetcher": "test_fetcher",
                        "height": "",
                        "size": 10,
                        "filters": None,
                        "type": "sql",
                        "smart": False,
                        "columns": [],
                        "depends_on": None,
                    }
                ],
                "widgets": [],
                "files": [{"name": "test_fetcher", "type": "sql", "source": None, "depends_on": []}],
            },
        }

        headers = {"access-token": "mock access token"}

        test_client.put("/page", json=data, headers=headers)

    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "file_name": "test_fetcher",
        "type": "sql",
    }

    # Act
    res = test_client.request("DELETE", "/files/", json=data)

    # Assert
    assert res.status_code == 200
    assert not workspace_file_exists("scripts/test_fetcher.sql")

    assert not verify_property_exists("tables[0].fetcher", "test_fetcher")
    assert verify_property_exists("tables[0].fetcher", "")


def test_rename_binded_fetcher(test_client):
    # Arrange
    if not workspace_file_exists("scripts/test_fetcher.sql"):
        data = copy.deepcopy(base_data)
        data["name"] = "test_fetcher"

        test_client.post("/files/", json=data)

        assert workspace_file_exists("scripts/test_fetcher.sql")

    if not verify_object_in_state_context("TablesState", "table2"):
        data = {
            "app_name": TEST_APP_NAME,
            "page_name": TEST_PAGE_NAME,
            "properties": {
                "tables": [
                    {
                        "label": "Table2",
                        "name": "table2",
                        "description": None,
                        "fetcher": "test_fetcher",
                        "height": "",
                        "size": 10,
                        "filters": None,
                        "type": "sql",
                        "smart": False,
                        "columns": [],
                        "depends_on": None,
                    }
                ],
                "widgets": [],
                "files": [{"name": "test_fetcher", "type": "sql", "source": None, "depends_on": []}],
            },
        }

        headers = {"access-token": "mock access token"}

        test_client.put("/page", json=data, headers=headers)

    data = {
        "app_name": TEST_APP_NAME,
        "page_name": TEST_PAGE_NAME,
        "old_name": "test_fetcher",
        "new_name": "test_new_fetcher",
        "type": "sql",
    }

    # Act
    res = test_client.put("/files/rename", json=data)

    # Assert
    assert res.status_code == 200
    assert not workspace_file_exists("scripts/test_fetcher.sql")
    assert workspace_file_exists("scripts/test_new_fetcher.sql")

    assert not verify_property_exists("tables[0].fetcher", "test_fetcher")
    assert verify_property_exists("tables[0].fetcher", "test_new_fetcher")
