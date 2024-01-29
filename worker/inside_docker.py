import importlib
import json
import os
import traceback

import pika

# TODO: move these to a shared location or put here
from dataframe import convert_df_to_resp_obj

# NOTE: helper scripts, duplicates of utils.py


def get_function_by_name(app_name: str, page_name: str, function_name: str):
    file_module = f"workspace.{app_name}.{page_name}.scripts.{function_name}"
    scripts = importlib.import_module(file_module)
    function = getattr(scripts, function_name)
    return function


def get_state_context(app_name: str, page_name: str, state: dict, context: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    State = getattr(page, "State")
    Context = getattr(page, "Context")
    return State(**state), Context(**context)


def get_state(app_name: str, page_name: str, state: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    State = getattr(page, "State")
    return State(**state)


# run data fetcher code
def run_python_query(app_name: str, page_name: str, file: dict, state: dict):
    try:
        state = get_state(app_name, page_name, state)
        args = {"state": state}
        function_name = get_function_by_name(app_name, page_name, file.get("name"))
        # call function
        df = function_name(**args)
        return convert_df_to_resp_obj(df), 200
    except Exception as e:
        return {"error": str(e)}, 500


connection = pika.BlockingConnection(pika.ConnectionParameters(host="host.docker.internal"))
channel = connection.channel()

try:
    # get evn variables
    app_name = os.getenv("app_name")
    page_name = os.getenv("page_name")
    state = json.loads(os.getenv("state"))
    file = json.loads(os.getenv("file"))

    # run python script and get result
    result = run_python_query(app_name, page_name, file, state)
    result = json.dumps(result, indent=2).encode("utf-8")

    # send result to rabbitmq
    channel.basic_publish(exchange="", routing_key="results", body=result)

except Exception as e:
    # catch any error and tracebacks and send to rabbitmq
    error_string = traceback.format_exc()
    channel.basic_publish(exchange="", routing_key="results", body=error_string + str(e))

connection.close()
