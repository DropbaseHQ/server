from server.tests.mocks.worker.python_subprocess import mock_run_process_task


def test_run_query(test_client, mocker):
    run_process_task = mock_run_process_task(True, {"columns": ["?column?"], "data": [[1]]}, "")
    mocker.patch("server.routers.query.run_process_task", side_effect=run_process_task)

    # Arrange
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "filter_sort": {},
        "file": {"name": "test_sql", "type": "sql", "source": "replica"},
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    }

    # Act
    res = test_client.post("/query", json=data)

    # Assert
    assert res.status_code == 200
    assert res.json()["success"]
