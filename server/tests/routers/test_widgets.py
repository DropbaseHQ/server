from server.tests.mocks.dropbase.widget import create_widget_response
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_widget_req(test_client, mocker):
    mocker.patch("server.requests.create_widget", create_widget_response)

    # Arrange
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
