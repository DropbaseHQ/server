from server.tests.mocks.dropbase.sync import sync_components_response
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_sync_table_columns_req(test_client):
    # FIXME
    return
    raise NotImplementedError("endpoint is broken in platform")


def test_sync_components_req(test_client, mocker):
    assert not workspace_object_exists("Context", "widgets.widget1.components.text1")
    mocker.patch("server.requests.sync_components", side_effect=sync_components_response)

    # Arrange
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
    }

    # Act
    res = test_client.post("/sync/components", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("Context", "widgets.widget1.components.text1")
