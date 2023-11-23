from server.tests.mocks.dropbase.widget import create_widget_response, update_widget_response
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_widget_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("widget", "create_widget", side_effect=create_widget_response)

    data = {
        "name": "test_widget",
        "property": {"name": "widget12", "description": ""},
        "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
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
    res = test_client.put("/widgets/4f1dabeb-907b-4e59-8417-ba67a801ba0e", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "widgets.widget12")
    assert not workspace_object_exists("Context", "widgets.widget12")
    assert workspace_object_exists("State", "widgets.widget13")
    assert workspace_object_exists("Context", "widgets.widget13")
