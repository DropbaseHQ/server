from server.tests.constants import PAGE_ID, WIDGET_ID
from server.tests.mocks.dropbase.widget import (
    create_widget_response,
    delete_widget_response,
    update_widget_response,
)
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_widget_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("widget", "create_widget", side_effect=create_widget_response)

    data = {
        "name": "test_widget",
        "property": {"name": "widget12", "description": ""},
        "page_id": PAGE_ID,
    }

    # Act
    res = test_client.post("/widgets", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "widgets.widget12")
    assert workspace_object_exists("Context", "widgets.widget12")


def test_update_widget_req(test_client, dropbase_router_mocker):
    # FIXME this test randomly fails
    # Arrange
    test_create_widget_req(test_client, dropbase_router_mocker)
    assert workspace_object_exists("State", "widgets.widget12")
    assert workspace_object_exists("Context", "widgets.widget12")

    dropbase_router_mocker.patch("widget", "update_widget", side_effect=update_widget_response)

    data = {
        "name": "widget13",
        "property": {"name": "widget13", "description": ""},
    }

    # Act
    res = test_client.put(f"/widgets/{WIDGET_ID}", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "widgets.widget12")
    assert not workspace_object_exists("Context", "widgets.widget12")
    assert workspace_object_exists("State", "widgets.widget13")
    assert workspace_object_exists("Context", "widgets.widget13")


def test_delete_widget_req(test_client, dropbase_router_mocker):
    # Arrange
    test_create_widget_req(test_client, dropbase_router_mocker)
    assert workspace_object_exists("State", "widgets.widget12")
    assert workspace_object_exists("Context", "widgets.widget12")

    dropbase_router_mocker.patch("widget", "delete_widget", side_effect=delete_widget_response)

    # Act
    res = test_client.delete(f"/widgets/{WIDGET_ID}")

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "widgets.widget12")
    assert not workspace_object_exists("Context", "widgets.widget12")
