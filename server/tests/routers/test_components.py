from server.tests.mocks.util import mock_response
from server.tests.mocks.dropbase.components import (
    create_component_response,
    update_component_response,
    delete_component_response,
)
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_component_req_text(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("component", "create_component", side_effect=create_component_response)

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


def test_create_component_req_select(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("component", "create_component", side_effect=create_component_response)

    data = {
        "property": {
            "name": "test_select",
            "label": None,
            "rules": None,
            "default": None,
            "required": None,
            "on_change": None,
            "validation": None
        },
        "widget_id": "abcdefg",
        "type": "select",
    }

    # Act
    res = test_client.post("/components", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "widgets.widget1.test_select")
    assert workspace_object_exists("Context", "widgets.widget1.components.test_select")


def test_create_component_req_input(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("component", "create_component", side_effect=create_component_response)

    data = {
        "property": {
            "name": "test_input",
            "type": "text",
            "label": None,
            "rules": None,
            "default": None,
            "required": None,
            "validation": None,
            "placeholder": None
        },
        "widget_id": "abcdefg",
        "type": "input",
    }

    # Act
    res = test_client.post("/components", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "widgets.widget1.test_input")
    assert workspace_object_exists("Context", "widgets.widget1.components.test_input")


def test_create_component_req_button(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("component", "create_component", side_effect=create_component_response)

    data = {
        "property": {"name": "test_button", "label": None, "visible": None, "on_click": None},
        "widget_id": "abcdefg",
        "type": "button",
    }

    # Act
    res = test_client.post("/components", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "widgets.widget1.test_button")
    assert workspace_object_exists("Context", "widgets.widget1.components.test_button")


def test_update_component_req(test_client, dropbase_router_mocker):
    # Arrange
    test_create_component_req_text(test_client, dropbase_router_mocker)
    dropbase_router_mocker.patch("component", "update_component", side_effect=update_component_response)

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


def test_delete_component_req(test_client, dropbase_router_mocker):
    # Arrange
    test_create_component_req_text(test_client, dropbase_router_mocker)
    dropbase_router_mocker.patch("component", "delete_component", side_effect=delete_component_response)

    # Act
    res = test_client.delete("/components/0617281c-c8bf-478e-b532-cb033e40a5ab")

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "widgets.widget1.test_text")
    assert not workspace_object_exists("Context", "widgets.widget1.components.test_text")


def test_delete_component_req_not_found(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch(
        "component",
        "delete_component",
        side_effect = lambda *args, **kwargs: mock_response(json={}, text="error", status_code=500)
    )

    # Act
    res = test_client.delete("/components/0617281c-c8bf-478e-b532-cb033e40a5ab")

    # Assert
    assert res.status_code != 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "widgets.widget1.test_text")
    assert not workspace_object_exists("Context", "widgets.widget1.components.test_text")
