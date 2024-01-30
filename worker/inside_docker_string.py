import ast
import importlib
import json
import os
import traceback
import uuid

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
        result = json.dumps(result.dict())
    if isinstance(result, dict) or isinstance(result, list):
        result = json.dumps(result)
    elif isinstance(result, pd.DataFrame):
        result = convert_df_to_resp_obj(result)
        result = json.dumps(result)
    else:
        result = str(result)

    # send result to redis
    r.set(job_id, result)
    r.expire(job_id, 60)

except Exception as e:
    error_string = traceback.format_exc()
    result = error_string + str(e)
    r.set(job_id, result)
    r.expire(job_id, 60)

finally:
    # remove temp file
    os.remove(file_name)
