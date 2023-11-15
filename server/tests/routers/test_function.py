def test_run_function(test_client):
    # Arrange
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "payload": {
            "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
            "context": {
                "widgets": {"widget1": {"components": {}}},
                "tables": {"table1": {"columns": {}}},
            },
        },
        "function_name": "test_function",
    }

    # Act
    res = test_client.post("/function", json=data)

    # Assert
    assert res.status_code == 200
    assert res.json()["success"]
    assert res.json()["stdout"] == "test\n"