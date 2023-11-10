def test_run_sql_string(test_client):
    # Arrange
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "file_content": "select 1;",
        "source": "replica",
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    }

    # Act
    res = test_client.post("/run_sql/run_sql_string", json=data)
    print(res.json())

    # Assert
    assert res.status_code == 200
    assert res.json()["success"]
