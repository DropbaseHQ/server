import copy

from server.tests.verify_property_exists import verify_object_exists
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
    data["properties"]["blocks"].append(
        {
            "block_type": "widget",
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

    # Assert
    assert res.status_code == 200
    assert verify_object_exists(APP_NAME, PAGE_NAME, "widget", "widget2")
    assert verify_object_in_state_context("State", "widget2")
    assert verify_object_in_state_context("Context", "widget2", True)


def test_create_widget_req_error_duplicate_names(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "widget",
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
    data["properties"]["blocks"].append(
        {
            "block_type": "widget",
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
    assert not verify_object_exists(APP_NAME, PAGE_NAME, "widget", "widget 2")
    assert not verify_object_in_state_context("State", "widget 2")
    assert res_data["detail"] == "Invalid widget names present in the table"


def test_create_widget_req_error_illegal_name_special_characters(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "widget",
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
    assert not verify_object_exists(APP_NAME, PAGE_NAME, "widget", "widget_2")
    assert not verify_object_in_state_context("State", "widget_2")
    assert res_data["detail"] == "Invalid widget names present in the table"


def test_create_widget_req_error_illegal_name_url_path(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "widget",
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
    assert not verify_object_exists(APP_NAME, PAGE_NAME, "widget", "../../widget2!")
    assert not verify_object_in_state_context("State", "../../")
    assert not verify_object_in_state_context("Context", "../../", True)
    assert res_data["detail"] == "Invalid widget names present in the table"


# NOTE: might need to change this, i don't understand how this checks for update
def test_update_widget_req(test_client, dropbase_router_mocker):
    dropbase_router_mocker.patch("auth", "get_user_permissions", side_effect=lambda *args, **kwargs: {})
    # Arrange
    data = copy.deepcopy(base_data)
    data["properties"]["blocks"].append(
        {
            "block_type": "widget",
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

    # Assert
    assert res.status_code == 200
    assert verify_object_exists(APP_NAME, PAGE_NAME, "widget", "widget3")
    assert verify_object_in_state_context("State", "widget3")
    assert verify_object_in_state_context("Context", "widget3", True)
