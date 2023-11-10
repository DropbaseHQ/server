def test_run_query(test_client):
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
