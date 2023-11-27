import copy
import os


def test_get_sources(test_client):
    try:
        # Arrange
        env_snapshot = {}
        new_env_vars = {
            "SOURCE_PG_SOURCE1_HOST": "localhost",
            "SOURCE_PG_SOURCE1_DATABASE": "source1",
            "SOURCE_PG_SOURCE1_USERNAME": "user",
            "SOURCE_PG_SOURCE1_PASSWORD":"pass",
            "SOURCE_PG_SOURCE1_PORT": "5432",
            "SOURCE_PG_SOURCE2_HOST": "localhost",
            "SOURCE_PG_SOURCE2_DATABASE": "source2",
            "SOURCE_PG_SOURCE2_USERNAME": "user",
            "SOURCE_PG_SOURCE2_PASSWORD":"pass",
            "SOURCE_PG_SOURCE2_PORT": "5432",
            "SOURCE_PG_SOURCEINVALID_HOST": "localhost",
            "SOURCE_PG_SOURCEINVALID_DATABASE": "source2",
            "SOURCE_PG_SOURCEINVALID_USERNAME": "user",
        }
        
        for key in os.environ.keys():
            if key.startswith("SOURCE_"):
                env_snapshot[key] = os.environ.pop(key)
        for key in new_env_vars.keys():
            os.environ[key] = new_env_vars[key]

        # Act
        res = test_client.get("/sources/")

        # Assert
        assert res.status_code == 200
        assert set(res.json()["sources"]) == {"source1", "source2"}
    finally:
        for key in new_env_vars.keys():
            if key in os.environ:
                del os.environ[key]
        for key in env_snapshot.keys():
            os.environ[key] = env_snapshot[key]