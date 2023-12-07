from server.tests.constants import PAGE_ID
from server.tests.mocks.dropbase.misc import sync_table_columns_response
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_sync_table_columns(test_client, mocker, dropbase_router_mocker):
    # Arrange
    mocker.patch("server.controllers.sync.get_table_columns", return_value=["col1", "col2"])
    dropbase_router_mocker.patch("misc", "sync_table_columns", side_effect=sync_table_columns_response)

    # Act
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "table": {
            "name": "table1",
            "property": {
                "filters": [],
                "appears_after": None,
                "on_row_change": None,
                "on_row_selection": None,
            },
            "page_id": PAGE_ID,
        },
        "file": {
            "name": "test_function_data_fetcher",
            "type": "data_fetcher",
            "source": "replica",
        },
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    }
    res = test_client.post("/sync/columns/", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "tables.table1")
    assert workspace_object_exists("Context", "tables.table1")
