import copy
import time

from server.controllers.properties import read_page_properties
from server.tests.verify_property_exists import get_objects_child_prop, verify_property_exists
from server.tests.verify_state_and_context import verify_object_in_state_context

APP_NAME = "dropbase_test_app"
PAGE_NAME = "page1"

base_data = {
    "app_name": APP_NAME,
    "page_name": PAGE_NAME,
    "properties": {
        "blocks": [
            {
                "block_type": "widget",
                "label": "Widget1",
                "name": "widget1",
                "description": None,
                "type": "base",
                "in_menu": True,
                "components": [
                    {
                        "label": "Button 1",
                        "name": "button1",
                        "color": None,
                        "on_click": None,
                        "display_rules": None,
                        "component_type": "button",
                    }
                ],
            }
        ],
        "files": [],
    },
}


def test_create_component_req_text(test_client, dropbase_router_mocker):
    # Arrange
    data = copy.deepcopy(base_data)
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    data["properties"]["blocks"][0]["components"].append(
        {
            "text": "Text 2",
            "name": "text2",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "text",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    assert res.status_code == 200

    # Assert
    assert verify_object_in_state_context("State", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "text2", True)

    properties = read_page_properties(APP_NAME, PAGE_NAME)
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "text2", "text")
        == "Text 2"
    )
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "text2", "name") == "text2"
    )
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "text2", "component_type")
        == "text"
    )


def test_create_component_req_select(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"][0]["components"].append(
        {
            "label": "Select 2",
            "name": "select2",
            "data_type": "string",
            "use_fetcher": False,
            "on_change": None,
            "display_rules": None,
            "component_type": "select",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    assert res.status_code == 200

    # assert isinstance(res_data.get("state").get("widgets").get("widget1"), dict)
    assert verify_object_in_state_context("State", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "select2", True)

    properties = read_page_properties(APP_NAME, PAGE_NAME)
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "select2", "label")
        == "Select 2"
    )
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "select2", "name")
        == "select2"
    )
    assert (
        get_objects_child_prop(
            properties, "widget", "widget1", "components", "select2", "component_type"
        )
        == "select"
    )


def test_create_component_req_input(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"][0]["components"].append(
        {
            "label": "Input 2",
            "name": "input2",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "input",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    assert res.status_code == 200

    assert verify_object_in_state_context("State", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "input2", True)

    properties = read_page_properties(APP_NAME, PAGE_NAME)
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "input2", "label")
        == "Input 2"
    )
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "input2", "name")
        == "input2"
    )
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "input2", "component_type")
        == "input"
    )


def test_create_component_req_button(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"][0]["components"].append(
        {
            "label": "Button 2",
            "name": "button2",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "button",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    assert res.status_code == 200

    # Assert
    assert verify_object_in_state_context("State", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "button2", True)

    properties = read_page_properties(APP_NAME, PAGE_NAME)
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "button2", "label")
        == "Button 2"
    )
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "button2", "name")
        == "button2"
    )
    assert (
        get_objects_child_prop(
            properties, "widget", "widget1", "components", "button2", "component_type"
        )
        == "button"
    )


def test_create_component_req_error_duplicate_names(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"][0]["components"].append(
        {
            "text": "Button 1",
            "name": "button1",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "text",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert res_data["detail"] == "A component with this name already exists"


def test_create_component_req_error_illegal_name_space_between(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"][0]["components"].append(
        {
            "label": "Button 2",
            "name": "button 2",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "button",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("Widget1ComponentsContext", "button 2", True)

    assert res_data["detail"] == "Invalid component names present in the table"


def test_create_component_req_error_illegal_name_special_characters(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"][0]["components"].append(
        {
            "label": "Button 2",
            "name": "button_2!",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "button",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("Widget1ComponentsContext", "button_2!", True)

    assert res_data["detail"] == "Invalid component names present in the table"


def test_create_component_req_error_illegal_name_url_path(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"][0]["components"].append(
        {
            "label": "Button 2",
            "name": "../../button2",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "button",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("Widget1ComponentsContext", "../../button2", True)

    assert res_data["detail"] == "Invalid component names present in the table"


def test_update_component_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"][0]["components"].append(
        {
            "label": "Button 3",
            "name": "button3",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "button",
        }
    )

    headers = {"access-token": "mock access token"}

    time.sleep(1)

    # Act
    res = test_client.put("/page", json=data, headers=headers)

    # Assert
    assert res.status_code == 200

    assert verify_object_in_state_context("State", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "button3", True)

    properties = read_page_properties(APP_NAME, PAGE_NAME)
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "button3", "label")
        == "Button 3"
    )
    assert (
        get_objects_child_prop(properties, "widget", "widget1", "components", "button3", "name")
        == "button3"
    )
    assert (
        get_objects_child_prop(
            properties, "widget", "widget1", "components", "button3", "component_type"
        )
        == "button"
    )


def test_delete_component_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)

    # Assert
    assert res.status_code == 200

    assert verify_object_in_state_context("State", "widget1")
    assert not verify_object_in_state_context("Widget1ComponentsContext", "button3", True)
