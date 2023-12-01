import unittest.mock

import pandas as pd


def test_run_python_query(test_client, mocker):
    # Arrange
    from server.controllers.run_python import run_python_query

    # Act
    output = run_python_query(
        app_name="dropbase_test_app",
        page_name="page1",
        file={"name": "test_function_data_fetcher", "type": "data_fetcher"},
        state={"widgets": {"widget1": {}}, "tables": {"table1": {}}},
        filter_sort={"filters": [], "sorts": []},
    )

    # Assert
    assert output["columns"] == ["x"]
    assert output["data"] == [[1]]
