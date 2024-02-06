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
        "function_name": "test_ui",
    }

    # Act
    res = test_client.post("/function", json=data)

    # Assert
    assert res.status_code == 202
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/query/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["type"] == "context"
    assert isinstance(res_data["context"], dict)


def test_run_function_not_found(test_client):
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
        "function_name": "nonexistent_function",
    }

    # Act
    res = test_client.post("/function", json=data)

    # Assert
    assert res.status_code != 200


def test_run_function_invalid_state_context(test_client):
    # Arrange
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "payload": {
            "state": {"widgets": {}, "tables": {}},
            "context": {
                "widgets": {"widget1": {"components": {}}},
                "tables": {},
            },
        },
        "function_name": "test_ui",
    }

    # Act
    res = test_client.post("/function", json=data)

    # Assert
    assert res.status_code == 202
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/query/status/{job_id}")
    assert res.status_code == 500
    res_data = res.json()
    assert res_data["type"] == "error"
