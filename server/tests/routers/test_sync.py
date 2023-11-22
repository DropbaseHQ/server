from server.tests.mocks.dropbase.sync import sync_components_response, sync_page_response
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


def test_sync_table_columns_req(test_client, dropbase_router_mocker):
    # TODO implement when mocking worker is figured out
    return
    dropbase_router_mocker.patch("misc", "sync_components", side_effect=sync_components_response)

    # Arrange
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
    }

    # Act
    res = test_client.post("/sync/columns/", json=data)

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

