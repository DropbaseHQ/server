import copy

from server.tests.verify_property_exists import verify_object_exists
from server.tests.verify_state_and_context import verify_object_in_state_context

APP_NAME = "dropbase_test_app"
PAGE_NAME = "page1"

base_data = {
    "app_name": APP_NAME,
    "page_name": PAGE_NAME,
    "properties": {
        "blocks": [
            {
                "block_type": "table",
                "label": "Table 1",
                "name": "table1",
                "description": None,
                "fetcher": None,
                "widget": None,
                "size": 10,
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
            "name": "table2",
            "label": "Table2",
            "type": "sql",
            "block_type": "table",
            "columns": [],
            "y": 0,
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)

    # Assert
    assert res.status_code == 200


def test_create_table_req_error_duplicate_names(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "name": "table1",
            "label": "Table1",
            "type": "sql",
            "block_type": "table",
            "columns": [],
            "y": 0,
        }
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
            "name": "table 2",
            "label": "Table 2",
            "type": "sql",
            "block_type": "table",
            "columns": [],
            "y": 0,
        }
    )
    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200
    assert res_data["detail"] == "Invalid table names present in the table"


def test_create_table_req_error_illegal_name_special_characters(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {"block_type": "table", "name": "table_2!", "label": "Table 2", "type": "sql", "columns": []}
    )
    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200
    assert res_data["detail"] == "Invalid table names present in the table"


def test_create_table_req_error_illegal_name_url_path(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {"block_type": "table", "name": "../../table2", "label": "Table 2", "type": "sql", "columns": []}
    )
    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200
    assert res_data["detail"] == "Invalid table names present in the table"


# NOTE: might need to change this, i don't understand how this checks for update
def test_update_table_req_file_changed(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "table",
            "name": "table3",
            "label": "Table 3",
            "type": "python",
            "columns": [],
        }
    )
    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)

    # Assert
    assert res.status_code == 200
    assert verify_object_exists(APP_NAME, PAGE_NAME, "table", "table3")
    assert verify_object_in_state_context("State", "table3")
    assert verify_object_in_state_context("Context", "table3", True)
