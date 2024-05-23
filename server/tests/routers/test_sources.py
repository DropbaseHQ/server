def test_get_sources(test_client):
    from server.config import worker_envs

    # Arrange
    databases = worker_envs.get("database")
    db_names = []
    for db_type in databases:
        for key in databases[db_type].keys():
            db_names.append(key)

    # Act
    res = test_client.get("/sources/")

    # Assert
    assert res.status_code == 200
    assert set(res.json()["sources"]) == set(db_names)
