import copy

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


def test_create_component_req_text(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
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

    # Act
    res = test_client.post("/page", json=data)
    res_data = res.json()

    # Assert
    assert isinstance(
        res_data.get("context").get("widgets").get("widget1").get("components").get("text2"),
        dict,
    )
    assert isinstance(res_data.get("state").get("widgets").get("widget1"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget1")
    assert verify_object_in_state_context("Widget1ComponentsContext", "text2", True)

    assert verify_property_exists("widgets[0].components[1].text", "Text 2")
    assert verify_property_exists("widgets[0].components[1].name", "text2")
    assert verify_property_exists("widgets[0].components[1].component_type", "text")


def test_create_component_req_select(test_client, dropbase_router_mocker):
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

    # Act
    res = test_client.post("/page", json=data)
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


def test_create_component_req_input(test_client):
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

    # Act
    res = test_client.post("/page", json=data)
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


def test_create_component_req_button(test_client):
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

    # Act
    res = test_client.post("/page", json=data)
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


def test_update_component_req(test_client, dropbase_router_mocker):
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

    # Act
    res = test_client.post("/page", json=data)
    res_data = res.json()

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
    # Arrange
    data = copy.deepcopy(base_data)

    # Act
    res = test_client.post("/page", json=data)

    # Assert
    assert res.status_code == 200

    assert verify_object_in_state_context("WidgetsState", "widget1")
    assert not verify_object_in_state_context("Widget1ComponentsContext", "button3", True)
