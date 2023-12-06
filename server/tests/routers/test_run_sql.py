from server.tests.mocks.controllers.python_subprocess import mock_run_process_task


def test_run_sql_string(test_client, mocker):
    # Arrange
    run_process_task = mock_run_process_task(True, {"columns": ["test_column"], "data": [[1]]}, "")
    mocker.patch("server.routers.run_sql.run_process_task", side_effect=run_process_task)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "file_content": "select 1;",
        "source": "replica",
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    }

    # Act
    res = test_client.post("/run_sql/run_sql_string", json=data)

    # Assert
    assert res.status_code == 200
    assert res.json()["success"]
