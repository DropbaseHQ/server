import copy

import pytest
from dotenv import load_dotenv

from server.tests.utils import setup_redis  # noqa

load_dotenv()


base_data = {
    "fetcher": "test_sql",
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "table_name": "table1",
    "state": {"table1": {}},
    "filter_sort": {"filters": [], "sorts": [], "pagination": {"page": 0, "page_size": 10}},
}


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_run_query_sql(test_client, mocker, mock_db):
    # Arrange
    data = copy.deepcopy(base_data)
    mocker.patch("server.controllers.run_sql.connect", return_value=mock_db)

    # Act
    res = test_client.post("/query", json=data)

    # Assert
    assert res.status_code == 202
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    assert isinstance(res_data["context"]["table1"]["data"]["data"], list)
    assert isinstance(res_data["context"]["table1"]["data"]["columns"], list)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_run_sql_string(mocker, test_client, mock_db):
    # Arrange

    mocker.patch("server.controllers.run_sql.connect", return_value=mock_db)
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "file_content": "select * from users;",
        "source": "local",
        "state": {"table1": {}},
    }

    # Act
    res = test_client.post("/query/string", json=data)

    # Assert
    assert res.status_code == 202
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    assert isinstance(res_data["data"], list)
    assert isinstance(res_data["columns"], list)
