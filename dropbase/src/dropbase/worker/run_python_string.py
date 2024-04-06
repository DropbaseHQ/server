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
from dotenv import load_dotenv

load_dotenv()


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


# TODO: move to class method
def write_file(
    file_code: str, test_code: str, state: dict, app_name: str, page_name: str, file_name: str = {}
):
    # TODO: can pass empty context directly since Context model is loaded in most cases
    python_str = file_code
    # NOTE: not all user functions will have state and context, so wrapping in try-except
    python_str += f"""
from dropbase.helpers.utils import get_empty_context

# initiate state model
state = {state}
state = State(**state)

# initiate empty context model
context = get_empty_context(app_name = "{app_name}", page_name = "{page_name}")
"""
    python_str += test_code

    with open(file_name, "w") as f:
        f.write(python_str)

    return python_str


def run(r, response):

    # get job id
    job_id = os.getenv("job_id")
    file_name = "f" + uuid.uuid4().hex + ".py"

    # redirect stdout
    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        state = json.loads(os.getenv("state") or "{}")
        app_name = os.getenv("app_name")
        page_name = os.getenv("page_name")
        file_code = os.getenv("file_code")
        test_code = os.getenv("test_code")

        # assign last expression to variable if needed
        test_code = assign_last_expression(test_code)

        # write exec file
        write_file(file_code, test_code, state, app_name, page_name, file_name)

        # import temp file
        module_name = file_name.split(".")[0]  # this gets you "temp_file"
        module = importlib.import_module(module_name)  # this imports the module
        result = module.result  # this gets the "result" from the module

        # convert result to json
        if result.__class__.__name__ == "Context":
            response["context"] = result.dict()
            response["type"] = "context"
        elif isinstance(result, pd.DataFrame):

            result = result.to_dtable()
            response["data"] = result["data"]
            response["columns"] = result["columns"]
            response["type"] = "table"
        else:
            response["data"] = result
            response["type"] = "generic"

        response["message"] = "Job has been completed"

    except Exception as e:
        response["type"] = "error"
        response["traceback"] = traceback.format_exc()
        response["message"] = str(e)

    finally:
        response["status_code"] = 200

        # get stdout
        response["stdout"] = redirected_output.getvalue()
        sys.stdout = old_stdout

        # send result to redis
        r.set(job_id, json.dumps(response))
        r.expire(job_id, 60)

        # remove temp file
        os.remove(file_name)
