import copy

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "table": {
        "label": "Table 1",
        "name": "table1",
        "description": None,
        "fetcher": "CUSTOM_FETCHER_GOES_HERE",
        "height": "",
        "size": 10,
        "filters": None,
        "type": "sql",
        "smart": False,
    },
    "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    "context": {
        "tables": {"table1": {"message": None, "message_type": None, "reload": False, "columns": {}}},
        "widgets": {},
    },
    "filter_sort": {"filters": [], "sorts": [], "pagination": {"page": 0, "page_size": 10}},
}


def test_run_query_sql(test_client, mocker, mock_db):
    # Arrange
    data = copy.deepcopy(base_data)
    data["table"]["fetcher"] = "test_sql"
    mocker.patch("server.controllers.run_sql.connect_to_user_db", return_value=mock_db)

    # Act
    res = test_client.post("/query", json=data)

    # Assert
    assert res.status_code == 200
    assert res.json()["success"]


def test_run_query_python(test_client):
    # Arrange
    data = copy.deepcopy(base_data)
    data["table"]["fetcher"] = "test_data_fetcher"

    # Act
    res = test_client.post("/query", json=data)

    # Assert
    assert res.status_code == 200
    res_data = res.json()["result"]
    assert res_data["columns"] == [{"name": "x", "column_type": "int64", "display_type": "integer"}]
    assert res_data["data"] == [[1]]
