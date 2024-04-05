import importlib
import json
import os
import time

from dotenv import load_dotenv

from server.tests.utils import setup_redis

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


def test_run_python_string():
    r = setup_redis()
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
    run_module.run(r, response)

    time.sleep(1)

    res = r.get(job_id)
    res_data = json.loads(res)

    # Assert
    assert res_data["status_code"] == 200

    assert res_data["context"]["page"]["message"] == PAGE_MESSAGE
    assert res_data["context"]["table1"]["data"]["columns"] == [
        {"name": "a", "data_type": "int64", "display_type": "integer"}
    ]
    assert res_data["context"]["table1"]["data"]["data"] == [[1], [2], [3]]
