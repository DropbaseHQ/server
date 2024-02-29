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
                "label": "Widget 1",
                "name": "widget1",
                "description": "description1",
                "components": [],
                "type": "base",
                "in_menu": True,
            }
        ],
        "files": [],
    },
}


def test_create_widget_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"].append(
        {
            "label": "Widget 2",
            "name": "widget2",
            "description": "description2",
            "components": [],
            "type": "base",
            "in_menu": True,
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("widgets").get("widget2"), dict)
    assert isinstance(res_data.get("state").get("widgets").get("widget2"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget2")
    assert verify_object_in_state_context("WidgetsContext", "widget2", True)

    assert verify_property_exists("widgets[1].label", "Widget 2")
    assert verify_property_exists("widgets[1].name", "widget2")


def test_create_widget_req_error_duplicate_names(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"].append(
        {
            "label": "Widget 1",
            "name": "widget1",
            "description": "description2",
            "components": [],
            "type": "base",
            "in_menu": True,
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert res_data["detail"] == "A widget with this name already exists"


def test_create_widget_req_error_illegal_name_space_between(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"].append(
        {
            "label": "Widget 2",
            "name": "widget 2",
            "description": "description2",
            "components": [],
            "type": "base",
            "in_menu": True,
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("WidgetsState", "widget 2")
    assert not verify_object_in_state_context("WidgetsContext", "widget 2", True)

    assert res_data["detail"] == "Invalid widget names present in the table"


def test_create_widget_req_error_illegal_name_special_characters(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"].append(
        {
            "label": "Widget 2",
            "name": "widget_2!",
            "description": "description2",
            "components": [],
            "type": "base",
            "in_menu": True,
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("WidgetsState", "widget_2!")
    assert not verify_object_in_state_context("WidgetsContext", "widget_2!", True)

    assert res_data["detail"] == "Invalid widget names present in the table"


def test_create_widget_req_error_illegal_name_url_path(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"].append(
        {
            "label": "Widget 2",
            "name": "../../widget2",
            "description": "description2",
            "components": [],
            "type": "base",
            "in_menu": True,
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not verify_object_in_state_context("WidgetsState", "../../widget2!")
    assert not verify_object_in_state_context("WidgetsContext", "../../", True)

    assert res_data["detail"] == "Invalid widget names present in the table"


def test_update_widget_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["widgets"].append(
        {
            "label": "Widget 3",
            "name": "widget3",
            "description": "description3",
            "components": [],
            "type": "base",
            "in_menu": True,
        }
    )

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code == 200

    assert isinstance(res_data.get("context").get("widgets").get("widget3"), dict)
    assert isinstance(res_data.get("state").get("widgets").get("widget3"), dict)

    assert verify_object_in_state_context("WidgetsState", "widget3")
    assert verify_object_in_state_context("WidgetsContext", "widget3", True)

    assert verify_property_exists("widgets[1].label", "Widget 3")
    assert verify_property_exists("widgets[1].name", "widget3")


def test_delete_widget_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)

    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=data, headers=headers)

    # Assert
    assert res.status_code == 200

    assert not verify_object_in_state_context("WidgetsState", "table3")
    assert not verify_object_in_state_context("WidgetsContext", "table3", True)
