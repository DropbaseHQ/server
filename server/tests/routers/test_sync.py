from server.tests.constants import PAGE_ID
from server.tests.mocks.dropbase.sync import (
    sync_components_response,
    sync_page_response,
    sync_table_columns_response,
)
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_get_state_context(test_client):
    # Act
    res = test_client.get("/sync/dropbase_test_app/page1")

    # Assert
    res_json = res.json()
    state = res_json["state"]
    context = res_json["context"]
    assert res.status_code == 200
    assert state["widgets"].get("widget1") is not None
    assert state["tables"].get("table1") is not None
    assert context["widgets"].get("widget1")
    assert context["tables"].get("table1")


def test_sync_table_columns_req(test_client, mocker, dropbase_router_mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.query.connect_to_user_db", return_value=mock_db)
    dropbase_router_mocker.patch("misc", "sync_table_columns", side_effect=sync_table_columns_response)

    # Act
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "table": {
            "name": "table1",
            "property": {
                "height": "",
                "filters": [],
                "appears_after": None,
                "on_row_change": None,
                "on_row_selection": None,
            },
            "page_id": "b3a1c199-3181-4683-85b7-a5a0060755d7",
            "date": "2023-12-01T23:20:29.134008",
            "file_id": "b21b973c-b83a-4ade-9e34-815e912bb7f0",
            "id": "2b331280-9f57-4b48-8b89-e83261e4b4fc",
            "depends_on": [],
        },
        "file": {
            "source": "local",
            "id": "b21b973c-b83a-4ade-9e34-815e912bb7f0",
            "date": "2023-12-11T20:50:14.248251",
            "page_id": "b3a1c199-3181-4683-85b7-a5a0060755d7",
            "name": "test_sql",
            "type": "sql",
        },
        "state": {
            "tables": {"table1": {"user_id": 1, "username": "John Doe"}},
            "widgets": {"widget1": {}},
        },
    }

    res = test_client.post(
        "/sync/columns/", json=data, cookies={"access_token_cookie": "mock access cookie"}
    )

    # Assert
    assert res.status_code == 200
    assert workspace_object_exists("State", "tables.table1.user_id")
    assert workspace_object_exists("State", "tables.table1.username")
    assert workspace_object_exists("State", "tables.table1.email")


def test_sync_components_req(test_client, dropbase_router_mocker):
    assert not workspace_object_exists("Context", "widgets.widget1.components.text1")
    dropbase_router_mocker.patch("misc", "sync_components", side_effect=sync_components_response)

    # Arrange
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
    }

    # Act
    res = test_client.post("/sync/components", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("Context", "widgets.widget1.components.text1")


def test_sync_page_state_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("sync", "sync_page", side_effect=sync_page_response)

    # Act
    res = test_client.put("/sync/page/0617281d-c8bf-478e-b532-cb033e40a5ab")

    # Assert
    assert res.status_code == 200
    assert not workspace_object_exists("Context", "widgets.widget1")
    assert workspace_object_exists("Context", "widgets.widget2")
