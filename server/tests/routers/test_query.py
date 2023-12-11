data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "file": {
        "source": "local",
        "id": "b21b973c-b83a-4ade-9e34-815e912bb7f0",
        "date": "2023-12-11T20:50:14.248251",
        "page_id": "b3a1c199-3181-4683-85b7-a5a0060755d7",
        "name": "test_sql",
        "type": "sql",
    },
    "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    "filter_sort": {"filters": [], "sorts": [], "pagination": {"page": 0, "page_size": 20}},
}


def test_run_query_sql(test_client, mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.query.connect_to_user_db", return_value=mock_db)

    # Act
    res = test_client.post("/query", json=data)

    # Assert
    assert res.status_code == 200
    assert res.json()["success"]


# TBI
def test_run_query_python(test_client, mocker):
    # Arrange
    # run_process_task = mock_run_process_task(True, {"columns": ["x"], "data": [[1]]}, "")
    # mocker.patch("server.routers.query.run_process_task", side_effect=run_process_task)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "filter_sort": {
            "filters": [],
            "sorts": [],
        },
        "file": {"name": "test_function_data_fetcher", "type": "data_fetcher"},
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    }

    # Act
    res = test_client.post("/query", json=data)

    # Assert
    assert res.status_code == 200
    assert res.json()["success"]
