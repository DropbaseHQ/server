from server.tests.mocks.dropbase.components import (
    create_component_response,
    update_component_response,
    delete_component_response,
)
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_component_req(test_client, mocker):
    # Arrange
    mocker.patch("server.requests.create_component", side_effect=create_component_response)

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


def test_update_component_req(test_client, mocker):
    # Arrange
    test_create_component_req(test_client, mocker)
    mocker.patch("server.requests.update_component", side_effect=update_component_response)

    data = {
        "property": {"name": "test_text_updated", "size": None, "text": None, "color": None},
        "type": "text",
    }

    # Act
    res = test_client.put("/components/0617281c-c8bf-478e-b532-cb033e40a5ab", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "widgets.widget1.test_text")
    assert not workspace_object_exists("Context", "widgets.widget1.components.test_text")
    assert workspace_object_exists("State", "widgets.widget1.test_text_updated")
    assert workspace_object_exists("Context", "widgets.widget1.components.test_text_updated")


def test_delete_component_req(test_client, mocker):
    # Arrange
    test_create_component_req(test_client, mocker)
    mocker.patch("server.requests.delete_component", side_effect=delete_component_response)

    # Act
    res = test_client.delete("/components/0617281c-c8bf-478e-b532-cb033e40a5ab")

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "widgets.widget1.test_text")
    assert not workspace_object_exists("Context", "widgets.widget1.components.test_text")
