def test_get_sources(test_client):
    from server.config import config

    # Arrange
    sources = config.get("sources")
    db_names = []
    for db_type in sources:
        for key in sources[db_type].keys():
            db_names.append(key)

    # Act
    res = test_client.get("/sources/")

    # Assert
    assert res.status_code == 200
    assert set(res.json()["sources"]) == set(db_names)
