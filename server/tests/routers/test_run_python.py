import importlib
import json
import os
import time

from dotenv import load_dotenv

from dropbase.helpers.utils import get_table_data_fetcher
from dropbase.schemas.files import DataFile
from server.controllers.properties import read_page_properties
from server.tests.utils import setup_redis  # noqa

load_dotenv()


PAGE_MESSAGE = "Hello World"
FILE_CODE = f"""from workspace.test_app.page1 import State, Context
from dropbase.helpers.dataframe import convert_df_to_resp_obj
import pandas as pd


def test(state: State, context: Context) -> Context:
    context.page.message = "{PAGE_MESSAGE}"
    df = pd.DataFrame({{\"a\": [1, 2, 3]}})
    context.table1.data = convert_df_to_resp_obj(df)
    return context
"""
TEST_CODE = "test(state,context)"
STATE = {"table1": {}}
APP_NAME = "dropbase_test_app"
PAGE_NAME = "page1"


def test_run_python_string(setup_redis):  # noqa
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
    os.environ["file_code"] = FILE_CODE
    os.environ["test_code"] = TEST_CODE
    os.environ["state"] = json.dumps(STATE)
    os.environ["app_name"] = APP_NAME
    os.environ["page_name"] = PAGE_NAME

    module_name = "dropbase.worker.run_python_string"

    run_module = importlib.import_module(module_name)

    # Act
    run_module.run(setup_redis, response)

    time.sleep(1)

    res = setup_redis.get(job_id)
    res_data = json.loads(res)

    # Assert
    assert res_data["status_code"] == 200

    assert res_data["context"]["page"]["message"] == PAGE_MESSAGE
    assert res_data["context"]["table1"]["data"]["columns"] == [
        {"name": "a", "data_type": "int64", "display_type": "integer"}
    ]
    assert res_data["context"]["table1"]["data"]["data"] == [[1], [2], [3]]


def test_run_python_datafetcher(setup_redis):  # noqa
    # Arrange
    job_id = "test_job_id"
    response = {"status_code": 202, "job_id": job_id}
    os.environ["app_name"] = APP_NAME
    os.environ["page_name"] = PAGE_NAME
    os.environ["job_id"] = job_id
    os.environ["state"] = json.dumps(STATE)

    properties = read_page_properties(APP_NAME, PAGE_NAME)
    file = get_table_data_fetcher(properties["files"], "test_data_fetcher")
    file = DataFile(**file)
    os.environ["file"] = json.dumps(file.dict())

    # Act
    module_name = "dropbase.worker.run_python_file"
    run_module = importlib.import_module(module_name)
    run_module.run(setup_redis, response)

    time.sleep(1)

    res = setup_redis.get(job_id)
    res_data = json.loads(res)

    # Assert
    assert res_data["status_code"] == 200
    assert res_data["context"]["table1"]["data"] == {
        "columns": [{"name": "a", "data_type": "int64", "display_type": "integer"}],
        "index": [0, 1, 2],
        "data": [[1], [2], [3]],
        "type": "python",
    }


def test_run_python_ui(setup_redis):  # noqa
    # Arrange
    job_id = "test_job_id"
    response = {"status_code": 202, "job_id": job_id}
    os.environ["app_name"] = APP_NAME
    os.environ["page_name"] = PAGE_NAME
    os.environ["job_id"] = job_id
    os.environ["state"] = json.dumps(STATE)

    properties = read_page_properties(APP_NAME, PAGE_NAME)
    file = get_table_data_fetcher(properties["files"], "test_ui")
    file = DataFile(**file)
    os.environ["file"] = json.dumps(file.dict())

    # Act
    module_name = "dropbase.worker.run_python_file"
    run_module = importlib.import_module(module_name)
    run_module.run(setup_redis, response)

    time.sleep(1)

    res = setup_redis.get(job_id)
    res_data = json.loads(res)

    # Assert
    assert res_data["status_code"] == 200
    assert res_data["context"]["page"]["message"] == "Test page message"
