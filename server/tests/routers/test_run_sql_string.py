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
    # assert False
    assert res.status_code == 200
    assert res.json()["success"]
