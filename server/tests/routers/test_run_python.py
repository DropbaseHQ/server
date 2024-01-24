def test_run_python_string(test_client):
    # Arrange
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "python_string": "print(0)\nx=3\nprint(1)\nprint(2)\nprint(x)",
        "payload": {
            "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
            "context": {
                "widgets": {"widget1": {"components": {}}},
                "tables": {"table1": {"columns": {}}},
            },
        },
        "file": {"name": "function1"},
    }

    # Act
    res = test_client.post("/query/python_string", json=data)

    # Assert
    assert res.status_code == 200
    assert res.json()["success"]
    assert res.json()["stdout"] == "0\n1\n2\n3\n"
