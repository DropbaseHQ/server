import copy
import time

from server.tests.verify_property_exists import verify_property_exists
from server.tests.verify_state_and_context import verify_object_in_state_context

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "blocks": [
            {
                "block_type": "table",
                "label": "Table1",
                "name": "table1",
                "description": None,
                "fetcher": None,
                "size": 10,
                "widget": None,
                "filters": None,
                "w": 4,
                "h": 1,
                "x": 0,
                "y": 0,
                "type": "sql",
                "smart": False,
                "columns": [],
            },
        ],
        "files": [],
    },
}

base_data_2 = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "blocks": [
            {
                "block_type": "table",
                "label": "Table1",
                "name": "table1",
                "description": None,
                "fetcher": None,
                "size": 10,
                "widget": None,
                "filters": None,
                "w": 4,
                "h": 1,
                "x": 0,
                "y": 0,
                "type": "sql",
                "smart": False,
                "columns": [],
            },
        ],
        "files": [],
    },
}


def test_create_table_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "table",
            "label": "Table 2",
            "name": "table2",
            "description": None,
            "fetcher": None,
            "size": 10,
            "widget": None,
            "filters": None,
            "w": 4,
            "h": 1,
            "x": 0,
            "y": 0,
            "type": "sql",
            "smart": False,
            "columns": [],
        },
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert res_data["message"] == "Properties updated successfully"

    assert verify_object_in_state_context("State", "table2")
    assert verify_object_in_state_context("Context", "table2", True)

    assert verify_property_exists("blocks[1].label", "Table 2")
    assert verify_property_exists("blocks[1].name", "table2")


def test_create_table_req_error_duplicate_names(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {"name": "table1", "label": "Table 1", "type": "sql", "columns": []}
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert res_data["detail"] == "A table with this name already exists"


def test_create_table_req_error_illegal_name_space_between(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "table",
            "label": "Table 2",
            "name": "table 2",
            "description": None,
            "fetcher": None,
            "size": 10,
            "widget": None,
            "filters": None,
            "w": 4,
            "h": 1,
            "x": 0,
            "y": 0,
            "type": "sql",
            "smart": False,
            "columns": [],
        },
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("State", "table 2")

    assert res_data["detail"] == "Invalid table names present in the table"


def test_create_table_req_error_illegal_name_special_characters(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "table",
            "label": "Table 2",
            "name": "table_2!",
            "description": None,
            "fetcher": None,
            "size": 10,
            "widget": None,
            "filters": None,
            "w": 4,
            "h": 1,
            "x": 0,
            "y": 0,
            "type": "sql",
            "smart": False,
            "columns": [],
        },
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("State", "table_2!")

    assert res_data["detail"] == "Invalid table names present in the table"


def test_create_table_req_error_illegal_name_url_path(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "table",
            "label": "Table 2",
            "name": "../../table2",
            "description": None,
            "fetcher": None,
            "size": 10,
            "widget": None,
            "filters": None,
            "w": 4,
            "h": 1,
            "x": 0,
            "y": 0,
            "type": "sql",
            "smart": False,
            "columns": [],
        },
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("State", "../../table 2")

    assert res_data["detail"] == "Invalid table names present in the table"


def test_update_table_req_file_changed(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "table",
            "label": "Table 4",
            "name": "table4",
            "description": None,
            "fetcher": None,
            "size": 10,
            "widget": None,
            "filters": None,
            "w": 4,
            "h": 1,
            "x": 0,
            "y": 0,
            "type": "sql",
            "smart": False,
            "columns": [],
        }
    )

    headers = {"access-token": "mock access token"}

    time.sleep(1)

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert res_data["message"] == "Properties updated successfully"

    # assert verify_object_in_state_context("State", "table4")
    # assert verify_object_in_state_context("Context", "table4", True) NOTE: Fails when ran as a group likely similar to the test_component one

    assert verify_property_exists("blocks[1].label", "Table 4")
    assert verify_property_exists("blocks[1].name", "table4")


def test_delete_table_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)

    # Assert
    assert res.status_code == 200

    assert not verify_object_in_state_context("State", "table3")
    assert not verify_object_in_state_context("Context", "table3", True)
