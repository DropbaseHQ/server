import copy
import time

from server.tests.verify_property_exists import verify_property_exists
from server.tests.verify_state_and_context import verify_object_in_state_context

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "tables": [],
        "widgets": [
            {
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
    data["properties"]["widgets"][0]["components"].append(
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
    test_client.put("/page", json=data, headers=headers)

    # Assert
    assert verify_object_in_state_context("WidgetsState", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "text2", True)

    assert verify_property_exists("widgets[0].components[1].text", "Text 2")
    assert verify_property_exists("widgets[0].components[1].name", "text2")
    assert verify_property_exists("widgets[0].components[1].component_type", "text")


def test_create_component_req_select(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"][0]["components"].append(
        {
            "label": "Select 2",
            "name": "select2",
            "color": None,
            "on_click": None,
            "display_rules": None,
            "component_type": "select",
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert isinstance(
        res_data.get("context").get("widgets").get("widget1").get("components").get("select2"),
        dict,
    )
    assert isinstance(res_data.get("state").get("widgets").get("widget1"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "select2", True)

    assert verify_property_exists("widgets[0].components[1].label", "Select 2")
    assert verify_property_exists("widgets[0].components[1].name", "select2")
    assert verify_property_exists("widgets[0].components[1].component_type", "select")


def test_create_component_req_input(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"][0]["components"].append(
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
    res_data = res.json()

    # Assert
    assert isinstance(
        res_data.get("context").get("widgets").get("widget1").get("components").get("input2"),
        dict,
    )
    assert isinstance(res_data.get("state").get("widgets").get("widget1"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "input2", True)

    assert verify_property_exists("widgets[0].components[1].label", "Input 2")
    assert verify_property_exists("widgets[0].components[1].name", "input2")
    assert verify_property_exists("widgets[0].components[1].component_type", "input")


def test_create_component_req_button(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"][0]["components"].append(
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
    res_data = res.json()

    # Assert
    assert isinstance(
        res_data.get("context").get("widgets").get("widget1").get("components").get("button2"),
        dict,
    )
    assert isinstance(res_data.get("state").get("widgets").get("widget1"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "button2", True)

    assert verify_property_exists("widgets[0].components[1].label", "Button 2")
    assert verify_property_exists("widgets[0].components[1].name", "button2")
    assert verify_property_exists("widgets[0].components[1].component_type", "button")


def test_create_component_req_error_duplicate_names(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch(
        "auth", "check_user_permissions", side_effect=lambda *args, **kwargs: {}
    )
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"][0]["components"].append(
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
    data["properties"]["widgets"][0]["components"].append(
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
    data["properties"]["widgets"][0]["components"].append(
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
    data["properties"]["widgets"][0]["components"].append(
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
    data["properties"]["widgets"][0]["components"].append(
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
    res_data = res.json()

    print(res_data)

    # Assert
    assert isinstance(
        res_data.get("context").get("widgets").get("widget1").get("components").get("button3"),
        dict,
    )
    assert isinstance(res_data.get("state").get("widgets").get("widget1"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "button3", True)

    assert verify_property_exists("widgets[0].components[1].label", "Button 3")
    assert verify_property_exists("widgets[0].components[1].name", "button3")
    assert verify_property_exists("widgets[0].components[1].component_type", "button")


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

    assert verify_object_in_state_context("WidgetsState", "widget1")
    assert not verify_object_in_state_context("Widget1ComponentsContext", "button3", True)
