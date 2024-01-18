from server.tests.constants import PAGE_ID, WIDGET_ID
from server.tests.mocks.dropbase.widget import (
    create_widget_response,
    delete_widget_response,
    update_widget_response,
)
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists
from server.tests.get_properties import get_properties

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "tables": [],
        "widgets": [
            {"label": "Widget 1", "name": "widget1", "description": "description1", "components": []}
        ],
        "files": [],
    },
}

def test_create_widget_req(test_client):
    # Arrange
    base_data["properties"]["widgets"].append(
        {"label": "Widget 2", "name": "widget2", "description": "description2", "components": []}
    )
    
    # Act
    res = test_client.post("/page", json=base_data)
    res_data = res.json()

    properties = get_properties(base_data)

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("widgets").get("widget2"), dict)
    assert isinstance(res_data.get("state").get("widgets").get("widget2"), dict)

    assert properties['widgets'][1]['label'] == 'Widget 2'
    assert properties['widgets'][1]['description'] == 'description2'

    assert is_valid_folder_structure()

    # assert workspace_object_exists("State", "widgets.widget1")
    # assert workspace_object_exists("Context", "widgets.widget1")


def test_update_widget_req(test_client):
    print(base_data)
    # Arrange
    base_data["properties"]["widgets"][1] = {"label": "Widget 3", "name": "widget3", "description": "description1", "components": []}

    # Act
    res = test_client.post("/page", json=base_data)
    res_data = res.json()

    properties = get_properties(base_data)

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("widgets").get("widget3"), dict)
    assert isinstance(res_data.get("state").get("widgets").get("widget3"), dict)

    assert properties['widgets'][1]['label'] == 'Widget 3'
    assert properties['widgets'][1]['name'] == 'widget3'

    assert is_valid_folder_structure()

    assert not workspace_object_exists("State", "widgets.widget2")
    assert not workspace_object_exists("Context", "widgets.widget2")

    # assert workspace_object_exists("State", "widgets.widget13")
    # assert workspace_object_exists("Context", "widgets.widget13")


def test_delete_widget_req(test_client, dropbase_router_mocker):
    # Arrange
    del base_data["properties"]["widgets"][1]

    # Act
    res = test_client.post("/page", json=base_data)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert is_valid_folder_structure()

    assert not workspace_object_exists("State", "widgets.widget3")
    assert not workspace_object_exists("Context", "widgets.widget3")
