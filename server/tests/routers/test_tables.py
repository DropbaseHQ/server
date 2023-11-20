from server.tests.mocks.dropbase.table import create_table_response
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_table_req(test_client, mocker):
    # Arrange
    mocker.patch("server.requests.create_table", side_effect=create_table_response)

    data = {
        "name": "test_table",
        "property": {
            "filters": [],
            "appears_after": None,
            "on_row_change": None,
            "on_row_selection": None,
        },
        "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
    }

    # Act
    res = test_client.post("/tables", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "tables.test_table")
    assert workspace_object_exists("Context", "tables.test_table")


def test_convert_table_req(test_client):
    # FIXME
    return
    raise NotImplementedError
