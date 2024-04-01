import copy
import importlib
import json
import os
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from server.tests.mocks.mock_classes import MockContext
from server.tests.utils import setup_redis

load_dotenv()

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "fetcher": "CUSTOMER_FETCHER_GOES_HERE",
    "state": {"table1": {}},
    "filter_sort": {"filters": [], "sorts": [], "pagination": {"page": 0, "page_size": 10}},
}


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_run_query_sql(test_client, mocker, mock_db):
    # Arrange
    data = copy.deepcopy(base_data)
    data["fetcher"] = "test_sql"
    mocker.patch("server.controllers.run_sql.connect", return_value=mock_db)

    # Act
    res = test_client.post("/query", json=data)

    # Assert
    assert res.status_code == 202
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/query/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["type"] == "table"
    assert isinstance(res_data["data"], list)
    assert isinstance(res_data["columns"], list)


def test_run_python_datafetcher(setup_redis):
    # Arrange
    job_id = "test_job_id"

    # Set env vars to use the run function
    os.environ["app_name"] = "dropbase_test_app"
    os.environ["page_name"] = "page1"
    os.environ["job_id"] = job_id
    os.environ["file"] = json.dumps({"type": "data_fetcher", "name": "test_data_fetcher_function"})
    os.environ["state"] = json.dumps({"widget1": {}, "table1": {}})

    with patch("dropbase.worker.run_python_file.get_function_by_name") as mock_get_function_by_name:

        def mock_data_fetcher_function(state):
            import pandas as pd

            return pd.DataFrame([[1]], columns=["x"])

        mock_get_function_by_name.return_value = mock_data_fetcher_function

        response = {
            "stdout": "",
            "traceback": "",
            "message": "",
            "type": "",
            "status_code": 202,
            "job_id": job_id,
        }

        # Call the run function
        module_name = "dropbase.worker.run_python_file"
        run_module = importlib.import_module(module_name)
        run_module.run(setup_redis, response)

        res = setup_redis.get(job_id)
        res_data = json.loads(res)

        assert res_data["status_code"] == 200
        assert res_data["job_id"] == "test_job_id"

        assert res_data["type"] == "table"
        assert res_data["columns"][0]["name"] == "x"
        assert res_data["columns"][0]["column_type"] == "python"
        assert res_data["columns"][0]["data_type"] == "int64"
        assert res_data["columns"][0]["display_type"] == "integer"

        assert res_data["data"] == [[1]]


def test_run_python_ui(setup_redis):
    # Arrange
    job_id = "test_job_id"

    # Set env vars to use the run function
    os.environ["app_name"] = "dropbase_test_app"
    os.environ["page_name"] = "page1"
    os.environ["job_id"] = job_id
    os.environ["file"] = json.dumps({"type": "ui", "name": "test_ui_function"})
    os.environ["state"] = json.dumps({"widget1": {}, "table1": {}})
    os.environ["context"] = json.dumps(
        {
            "page": {},
            "widget1": {
                "components": {  # NOTE: We need these components when ran in groups or else it will raise a validator error
                    "button1": {},
                    "text2": {},
                }
            },
            "table1": {"columns": {}},
        }
    )

    with patch("dropbase.worker.run_python_file.get_function_by_name") as mock_get_function_by_name:

        def mock_data_fetcher_function(state, context):
            return MockContext(updated_state=state, updated_context=context)

        mock_get_function_by_name.return_value = mock_data_fetcher_function

        response = {
            "stdout": "",
            "traceback": "",
            "message": "",
            "type": "",
            "status_code": 202,
            "job_id": job_id,
        }

        # Call the run function
        module_name = "dropbase.worker.run_python_file"
        run_module = importlib.import_module(module_name)
        run_module.run(setup_redis, response)

        res = setup_redis.get(job_id)
        res_data = json.loads(res)

        print(res_data)

        assert res_data["status_code"] == 200
        assert res_data["job_id"] == "test_job_id"

        assert res_data["type"] == "context"
        assert res_data["context"] == {"context": "mock_context"}
