import unittest.mock

import pandas as pd


def test_run_sql_query(test_client, mocker):
    # Arrange
    mock_df = pd.DataFrame(data=[[1]], columns=["?column?"])
    mocker.patch("server.worker.run_sql.run_df_query", return_value=mock_df)
    from server.controllers.run_sql import run_sql_query

    # Act
    output = run_sql_query(
        app_name="dropbase_test_app",
        page_name="page1",
        file={"name": "test_sql", "type": "sql", "source": "mock_db"},
        state={"widgets": {"widget1": {}}, "tables": {"table1": {}}},
        filter_sort={"filters": [], "sorts": []},
    )

    # Assert
    assert output["columns"] == ["?column?"]
    assert output["data"] == [[1]]


def test_run_sql_from_string(test_client, mocker):
    # Arrange
    mock_df = pd.DataFrame(data=[[1]], columns=["?column?"])
    mocker.patch("server.worker.run_sql.run_df_query", return_value=mock_df)
    from server.controllers.run_sql import run_sql_from_string

    # Act
    output = run_sql_from_string(
        app_name="dropbase_test_app",
        page_name="page1",
        file_content="select 1;",
        state={"widgets": {"widget1": {}}, "tables": {"table1": {}}},
        source="mock_db",
    )

    # Assert
    assert output["columns"] == ["?column?"]
    assert output["data"] == [[1]]
