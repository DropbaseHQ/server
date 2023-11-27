from server.tests.mocks.dropbase.sync import sync_components_response, sync_page_response
from server.tests.mocks.worker.python_subprocess import mock_run_process_task
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


def test_sync_table_columns_req(test_client, mocker):
    # Arrange
    run_process_task = mock_run_process_task(True, {"message": "success"}, "")
    mocker.patch("server.routers.query.run_process_task", side_effect=run_process_task)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "table": {
            "name": "table1",
            "property": {
                "filters": [],
                "appears_after": None,
                "on_row_change": None,
                "on_row_selection": None,
            },
            "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
        },
        "file": {
            "name": "test_sql",
            "type": "sql",
            "source": "replica",
        },
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    }

    # Act
    res = test_client.post("/sync/columns/", json=data, cookies={"access_token_cookie": "mock access cookie"})

    # Assert
    assert res.status_code == 200


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

