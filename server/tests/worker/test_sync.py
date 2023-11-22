import unittest.mock

import pandas as pd

from server.tests.mocks.dropbase.misc import sync_table_columns_response


def test_sync_table_columns(test_client, mocker):
    # Arrange
    mock_router = unittest.mock.MagicMock()
    mock_router.misc.sync_table_columns.side_effect = sync_table_columns_response
    mocker.patch("server.worker.sync.DropbaseRouter", return_value=mock_router)
    mocker.patch("server.controllers.query.query_db", side_effect=lambda *args: pd.DataFrame([[1]], columns=["?column?"]))

    from server.worker.sync import sync_table_columns

    # Act
    output = sync_table_columns(
        app_name="dropbase_test_app",
        page_name="page1",
        table={
            "name": "table1",
            "property": {
                "filters": [],
                "appears_after": None,
                "on_row_change": None,
                "on_row_selection": None,
            },
            "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
        },
        file={
            "name": "test_sql",
            "type": "sql",
            "source": "replica",
        },
        state={"widgets": {"widget1": {}}, "tables": {"table1": {}}},
        access_cookies=None,
    )

    # Assert
    assert output["message"] == "success"