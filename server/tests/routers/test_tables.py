import copy

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


def test_create_table_req(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["tables"].append(
        {"name": "table2", "label": "Table 2", "type": "sql", "columns": []}
    )

    # Act
    res = test_client.post("/page", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("tables").get("table2"), dict)
    assert isinstance(res_data.get("state").get("tables").get("table2"), dict)

    assert verify_object_in_state_context("TablesState", "table2")
    assert verify_object_in_state_context("TablesContext", "table2", True)


def test_update_table_req_file_changed(test_client):
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

    # Act
    res = test_client.post("/page", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("tables").get("table3"), dict)
    assert isinstance(res_data.get("state").get("tables").get("table3"), dict)

    assert verify_object_in_state_context("TablesState", "table3")
    assert verify_object_in_state_context("TablesContext", "table3", True)


def test_delete_table_req(test_client):
    # Arrange
    data = copy.deepcopy(base_data)

    # Act
    res = test_client.post("/page", json=data)

    # Assert
    assert res.status_code == 200

    assert not verify_object_in_state_context("TablesState", "table3")
    assert not verify_object_in_state_context("TablesContext", "table3", True)
