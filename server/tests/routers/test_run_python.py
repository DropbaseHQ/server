import importlib
import json
import os
import time
from unittest.mock import patch

import pytest
import redis
from dotenv import load_dotenv

from server.tests.constants import TEST_APP_NAME, TEST_PAGE_NAME

load_dotenv()


@pytest.fixture(scope="session")
def setup_redis():
    r = redis.Redis(host="localhost", port=6379, db=0)
    return r


def test_run_python_string(setup_redis):
    # Arrange
    os.environ["type"] = "string"
    job_id = "test_job_id"
    response = {
        "stdout": "",
        "traceback": "",
        "message": "",
        "type": "",
        "status_code": 202,
        "job_id": job_id,
    }

    # Set env vars to use the run function
    os.environ["job_id"] = job_id
    os.environ[
        "file_code"
    ] = 'import pandas as pd\ndef test_data_fetcher(): return pd.DataFrame(data=[[1]], columns=["x"])'
    os.environ["test_code"] = "test_data_fetcher()"
    os.environ["state"] = json.dumps({"tables": {"table1": {}}, "widgets": {}})
    os.environ["context"] = json.dumps(
        {
            "tables": {
                "table1": {"message": None, "message_type": None, "reload": False, "columns": {}}
            },
            "widgets": {},
        }
    )

    if os.getenv("type") == "string":
        module_name = "dropbase.worker.run_python_string"
    else:
        module_name = "dropbase.worker.run_python_file"

    run_module = importlib.import_module(module_name)

    # Act
    run_module.run(setup_redis, response)

    time.sleep(1)

    res = setup_redis.get(job_id)
    res_data = json.loads(res)

    # Assert
    assert res_data["status_code"] == 200

    assert res_data.get("type") == "table"

    assert res_data["columns"][0]["name"] == "x"
    assert res_data["columns"][0]["column_type"] == "python"
    assert res_data["columns"][0]["data_type"] == "int64"
    assert res_data["columns"][0]["display_type"] == "integer"
    assert res_data["data"] == [[1]]
