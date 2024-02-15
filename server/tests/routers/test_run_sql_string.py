import pytest


@pytest.mark.parametrize("mock_db", ["postgres", "snowflake"], indirect=True)
def test_run_sql_string(mocker, test_client, mock_db):
    # Arrange

    mocker.patch("server.controllers.run_sql.connect_to_user_db", return_value=mock_db)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "file_content": "select * from users;",
        "source": "local",
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    }

    # Act
    res = test_client.post("/query/sql_string", json=data)

    # Assert
    assert res.status_code == 202
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/query/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    print(res_data)
    assert res_data["type"] == "table"
    assert isinstance(res_data["data"], list)
    assert isinstance(res_data["columns"], list)
