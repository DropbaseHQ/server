from server.tests.mocks.dropbase.widget import create_widget_response, update_widget_response
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_widget_req(test_client, mocker):
    # Arrange
    mocker.patch("server.requests.create_widget", create_widget_response)

    data = {
        "name": "test_widget",
        "property": {"name": "widget12", "description": ""},
        "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
    }

    # Act
    res = test_client.post("/widgets", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "widgets.widget12")
    assert workspace_object_exists("Context", "widgets.widget12")


def test_update_widget_req(test_client, mocker):
    # Arrange
    test_create_widget_req(test_client, mocker)
    assert workspace_object_exists("State", "widgets.widget12")
    assert workspace_object_exists("Context", "widgets.widget12")

    mocker.patch("server.requests.update_widget", update_widget_response)

    data = {
        "name": "widget13",
        "property": {"name": "widget13", "description": ""},
    }

    # Act
    res = test_client.put("/widgets/4f1dabeb-907b-4e59-8417-ba67a801ba0e", json=data)

    # FIXME might be a data race between updating state file and the asserts below
    import time;time.sleep(5)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "widgets.widget12")
    assert not workspace_object_exists("Context", "widgets.widget12")
    assert workspace_object_exists("State", "widgets.widget13")
    assert workspace_object_exists("Context", "widgets.widget13")
