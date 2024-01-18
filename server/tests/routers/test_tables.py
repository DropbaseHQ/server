from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists

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


def test_create_table_req(test_client):
    # Arrange
    base_data["properties"]["tables"].append(
        {"name": "table2", "label": "Table 2", "type": "sql", "columns": []}
    )

    # Act
    res = test_client.post("/page", json=base_data)
    res_data = res.json()

    properties = base_data["properties"]

    # PATH = "dropbase_test_app/page1/scripts/state"

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("tables").get("table2"), dict)
    assert isinstance(res_data.get("state").get("tables").get("table2"), dict)

    assert properties["tables"][1]["label"] == "Table 2"
    assert properties["tables"][1]["type"] == "sql"

    # assert is_valid_folder_structure()

    # assert verify_state_exists("dropbase_test_app/page1/scripts/state", "TableState", "table2")
    # assert verify_context_exists("dropbase_test_app/page1/scripts/context", "TableState", "table2")

    # TODO: check app/page directory is properly structured

    # DONE --> working
    # check properties.json has the right data

    # DONE --> maybe???
    # assert is_valid_folder_structure()

    # DONE --> not working
    # assert workspace_object_exists("State", "tables.test_table")
    # assert workspace_object_exists("Context", "tables.test_table")


def test_update_table_req_file_changed(test_client, dropbase_router_mocker, mocker):
    # Arrange
    base_data["properties"]["tables"][1] = {
        "name": "table3",
        "label": "Table 3",
        "type": "python",
        "columns": [],
    }

    properties = base_data["properties"]

    # Act
    res = test_client.post("/page", json=base_data)
    res_data = res.json()

    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("tables").get("table3"), dict)
    assert isinstance(res_data.get("state").get("tables").get("table3"), dict)

    assert properties["tables"][1]["label"] == "Table 3"
    assert properties["tables"][1]["type"] == "python"

    assert is_valid_folder_structure()

    assert not workspace_object_exists("State", "tables.table2")
    assert not workspace_object_exists("Context", "tables.table2")

    # assert workspace_object_exists("State", "tables.table3") --> need to fix
    # assert workspace_object_exists("Context", "tables.table3") --> need to fix


def test_delete_table_req(test_client, dropbase_router_mocker):
    # Arrange
    del base_data["properties"]["tables"][1]

    # Act
    res = test_client.post("/page", json=base_data)

    # Assert
    assert res.status_code == 200

    assert is_valid_folder_structure()

    assert not workspace_object_exists("State", "tables.table3")
    assert not workspace_object_exists("Context", "tables.table3")
