import importlib
import json
import os
import traceback

import redis

# TODO: move these to a shared location or put here
from dataframe import convert_df_to_resp_obj

# NOTE: helper scripts, duplicates of utils.py


def get_function_by_name(app_name: str, page_name: str, function_name: str):
    file_module = f"workspace.{app_name}.{page_name}.scripts.{function_name}"
    scripts = importlib.import_module(file_module)
    function = getattr(scripts, function_name)
    return function


def get_state(app_name: str, page_name: str, class_dict: dict, class_name: str = "State"):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    ClassName = getattr(page, class_name)
    return ClassName(**class_dict)


# run data fetcher code
def run_python_data_fetcher(app_name: str, page_name: str, file: dict, state: dict):
    state = get_state(app_name, page_name, state, "State")
    args = {"state": state}
    function_name = get_function_by_name(app_name, page_name, file.get("name"))
    # call function
    df = function_name(**args)
    return convert_df_to_resp_obj(df)


# for ui functions
def run_python_ui(app_name: str, page_name: str, file: dict, state: dict, context: dict):
    state = get_state(app_name, page_name, state, "State")
    context = get_state(app_name, page_name, context, "Context")
    args = {"state": state, "context": context}
    function_name = get_function_by_name(app_name, page_name, file.get("name"))
    # call function
    context = function_name(**args)
    return context.dict()


r = redis.Redis(host="host.docker.internal", port=6379, db=0)


try:
    # get evn variables
    app_name = os.getenv("app_name")
    page_name = os.getenv("page_name")
    state = json.loads(os.getenv("state"))
    file = json.loads(os.getenv("file"))
    job_id = os.getenv("job_id")

    # run python script and get result
    if file["type"] == "ui":
        result = run_python_ui(app_name, page_name, file, state)
    elif file["type"] == "data_fetcher":
        result = run_python_data_fetcher(app_name, page_name, file, state)

    result = json.dumps(result)

    # send result to redis
    r.set(job_id, result)
    r.expire(job_id, 60)

except Exception as e:
    # catch any error and tracebacks and send to rabbitmq
    error_string = traceback.format_exc()
    result = error_string + str(e)
    r.set(job_id, result)
    r.expire(job_id, 60)
