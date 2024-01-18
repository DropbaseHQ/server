import copy

from server.tests.verify_state_and_context import verify_object_in_state_context
from server.tests.verify_property_exists import verify_property_exists

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "tables": [],
        "widgets": [
            {
                "label": "Widget 1",
                "name": "widget1",
                "description": "description1",
                "components": [],
            }
        ],
        "files": [],
    },
}


def test_create_widget_req(test_client):
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"].append(
        {
            "label": "Widget 2",
            "name": "widget2",
            "description": "description2",
            "components": [],
        }
    )

    # Act
    res = test_client.post("/page", json=data)
    res_data = res.json()

    print(res_data)

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("widgets").get("widget2"), dict)
    assert isinstance(res_data.get("state").get("widgets").get("widget2"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget2")
    assert verify_object_in_state_context("WidgetsContext", "widget2", True)

    assert verify_property_exists("widgets[1].label", "Widget 2")
    assert verify_property_exists("widgets[1].name", "widget2")


def test_update_widget_req(test_client):
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"].append(
        {
            "label": "Widget 3",
            "name": "widget3",
            "description": "description3",
            "components": [],
        }
    )

    # Act
    res = test_client.post("/page", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("widgets").get("widget3"), dict)
    assert isinstance(res_data.get("state").get("widgets").get("widget3"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget3")
    assert verify_object_in_state_context("WidgetsContext", "widget3", True)

    assert verify_property_exists("widgets[1].label", "Widget 3")
    assert verify_property_exists("widgets[1].name", "widget3")


def test_delete_widget_req(test_client):
    data = copy.deepcopy(base_data)

    # Act
    res = test_client.post("/page", json=data)

    # Assert
    assert res.status_code == 200

    assert not verify_object_in_state_context("WidgetsState", "table3")
    assert not verify_object_in_state_context("WidgetsContext", "table3", True)
