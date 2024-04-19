import copy

import pytest

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "table_name": "table1",
    "fetcher": "test_sql",
    "state": {"table1": {}},
    "filter_sort": {"filters": [], "sorts": [], "pagination": {"page": 0, "page_size": 10}},
}


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_query_db(mocker, mock_db):
    # Arrange
    mocker.patch("dropbase.database.connect.connect", return_value=mock_db)

    # Act
    output = mock_db._run_query("select * from users;", {})

    # Assert
    # TODO: improve assertions
    assert len(output) > 0
    assert len(output[0]) > 0


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_apply_filters(test_client, mocker, mock_db):
    # Arrange
    data = copy.deepcopy(base_data)
    data["filter_sort"]["filters"] = [
        {
            "column_name": "user_id",
            "value": 1,
            "condition": "=",
            "id": "ee446ffd-6427-4118-be46-4f2971c94b7d",
            "column_type": "integer",
        }
    ]

    mocker.patch("server.controllers.run_sql.connect", return_value=mock_db)

    # Act
    res = test_client.post("/query", json=data)
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    assert isinstance(res_data["context"]["table1"]["data"]["data"], list)
    assert isinstance(res_data["context"]["table1"]["data"]["columns"], list)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_apply_sorts(test_client, mocker, mock_db):
    # Arrange
    data = copy.deepcopy(base_data)
    data["filter_sort"]["sorts"] = [{"column_name": "user_id", "value": "desc"}]

    mocker.patch("server.controllers.run_sql.connect", return_value=mock_db)

    # Act
    res = test_client.post("/query", json=data)
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    # assert res_data["type"] == "table"
    assert isinstance(res_data["context"]["table1"]["data"]["data"], list)
    assert isinstance(res_data["context"]["table1"]["data"]["columns"], list)
