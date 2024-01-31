import ast
import importlib
import json
import os
import sys
import traceback
import uuid
from io import StringIO

import astor
import pandas as pd
import redis
from dataframe import convert_df_to_resp_obj


def assign_last_expression(script: str) -> str:
    """
    get test code and assign last expression to a variable named result
    """
    module = ast.parse(script)

    if module.body:
        # get the last statement
        last_statement = module.body[-1]

        # Replace Expr statement with assignment to "result"
        assign = ast.Assign(targets=[ast.Name(id="result", ctx=ast.Store())], value=last_statement.value)
        module.body[-1] = assign

    # Transform the AST back to Python code
    return astor.to_source(module)


def write_file(file_code: str, test_code: str, state: dict, context: dict = {}, file_name: str = {}):
    python_str = file_code
    # NOTE: not all user functions will have state and context, so wrapping in try-except
    python_str += f"""
state = {state}
context = {context}

try:
    state = State(**state)
except:
    pass

try:
    context = Context(**context)
except:
    pass
"""
    python_str += test_code

    with open(file_name, "w") as f:
        f.write(python_str)

    return python_str


r = redis.Redis(host="host.docker.internal", port=6379, db=0)

# get job id
job_id = os.getenv("job_id")
file_name = "f" + uuid.uuid4().hex + ".py"

old_stdout = sys.stdout
redirected_output = StringIO()
sys.stdout = redirected_output
response = {"stdout": "", "traceback": "", "message": "", "type": "", "status_code": 202}

try:
    state = json.loads(os.getenv("state") or "{}")
    context = json.loads(os.getenv("context") or "{}")
    file_code = os.getenv("file_code")
    test_code = os.getenv("test_code")

    # assign last expression to variable if needed
    test_code = assign_last_expression(test_code)

    # write exec file
    write_file(file_code, test_code, state, context, file_name)

    # import temp file
    module_name = file_name.split(".")[0]  # this gets you "temp_file"
    module = importlib.import_module(module_name)  # this imports the module
    result = module.result  # this gets the "result" from the module

    # convert result to json
    if result.__class__.__name__ == "Context":
        response["context"] = result.dict()
        response["type"] = "context"
    elif isinstance(result, pd.DataFrame):
        result = convert_df_to_resp_obj(result)
        response["data"] = result["data"]
        response["columns"] = result["columns"]
        response["type"] = "table"
    elif isinstance(result, dict) or isinstance(result, list):
        result = json.dumps(result)
        response["data"] = result
        response["type"] = "generic"
    else:
        response["data"] = str(result)
        response["type"] = "generic"

    response["status_code"] = 200
    response["message"] = "Job has been completed"

except Exception as e:
    response["type"] = "error"
    response["status_code"] = 500
    response["traceback"] = traceback.format_exc()
    response["message"] = str(e)

finally:
    # send result to redis
    r.set(job_id, json.dumps(response))
    r.expire(job_id, 60)

    # remove temp file
    stdout = redirected_output.getvalue()
    sys.stdout = old_stdout
    os.remove(file_name)
