import copy
import time

from server.tests.verify_property_exists import verify_property_exists
from server.tests.verify_state_and_context import verify_object_in_state_context

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "tables": [
            {"name": "table1", "label": "Table 1", "type": "sql", "columns": []},
        ],
        "widgets": [],
        "files": [],
    },
}


def test_create_table_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["tables"].append(
        {"name": "table2", "label": "Table 2", "type": "sql", "columns": []}
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("tables").get("table2"), dict)
    assert isinstance(res_data.get("state").get("tables").get("table2"), dict)

    assert verify_object_in_state_context("TablesState", "table2")
    assert verify_object_in_state_context("TablesContext", "table2", True)

    assert verify_property_exists("tables[1].label", "Table 2")
    assert verify_property_exists("tables[1].name", "table2")


def test_create_table_req_error_duplicate_names(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["tables"].append(
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
    data["properties"]["tables"].append(
        {"name": "table 2", "label": "Table 2", "type": "sql", "columns": []}
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("TablesState", "table 2")

    assert res_data["detail"] == "Invalid table names present in the table"


def test_create_table_req_error_illegal_name_special_characters(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["tables"].append(
        {"name": "table_2!", "label": "Table 2", "type": "sql", "columns": []}
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("TablesState", "table_2!")

    assert res_data["detail"] == "Invalid table names present in the table"


def test_create_table_req_error_illegal_name_url_path(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["tables"].append(
        {"name": "../../table2", "label": "Table 2", "type": "sql", "columns": []}
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("TablesState", "../../table 2")

    assert res_data["detail"] == "Invalid table names present in the table"


def test_update_table_req_file_changed(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["tables"].append(
        {
            "name": "table3",
            "label": "Table 3",
            "type": "python",
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

    assert isinstance(res_data.get("context").get("tables").get("table3"), dict)
    assert isinstance(res_data.get("state").get("tables").get("table3"), dict)

    assert verify_object_in_state_context("TablesState", "table3")
    assert verify_object_in_state_context("TablesContext", "table3", True)

    assert verify_property_exists("tables[1].label", "Table 3")
    assert verify_property_exists("tables[1].name", "table3")


def test_delete_table_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)

    # Assert
    assert res.status_code == 200

    assert not verify_object_in_state_context("TablesState", "table3")
    assert not verify_object_in_state_context("TablesContext", "table3", True)
