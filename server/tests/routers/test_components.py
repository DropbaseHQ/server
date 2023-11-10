from server.tests.mocks.dropbase.components import create_component_response
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_component_req(test_client, mocker):
    mocker.patch("server.requests.create_component", side_effect=create_component_response)

    # Arrange
    data = {
        "property": {"name": "test_text", "size": None, "text": None, "color": None},
        "widget_id": "abcdefg",
        "type": "text",
    }

    # Act
    res = test_client.post("/components", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "widgets.widget1.test_text")
    assert workspace_object_exists("Context", "widgets.widget1.components.test_text")
