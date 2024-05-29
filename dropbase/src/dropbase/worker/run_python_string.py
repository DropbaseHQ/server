import ast
import importlib
import json
import os
import traceback
import uuid

import astor
from dotenv import load_dotenv

load_dotenv()


def run(r):

    try:
        response = {"stdout": "", "traceback": "", "message": "", "type": "", "status_code": 202}
        # read state and context
        state = json.loads(os.getenv("state"))
        code = os.getenv("code")
        test = os.getenv("test")

        code_str = compose_code(code, test, state)
        code_str = assign_last_expression(code_str)

        file_name = "f" + uuid.uuid4().hex + ".py"
        with open(file_name, "w") as f:
            f.write(code_str)

        # import temp file
        module_name = file_name.split(".")[0]  # this gets you "temp_file"
        module = importlib.import_module(module_name)  # this imports the module
        result = module.result  # this gets the "result" from the module

        # convert result to json
        if result.__class__.__name__ == "Context":
            response["context"] = result.dict()
            response["type"] = "context"
        else:
            response["data"] = result
            response["type"] = "generic"

        response["message"] = "Job has been completed"
        response["message"] = "job completed"
        response["status_code"] = 200
    except Exception as e:
        # catch any error and tracebacks and send to rabbitmq
        response["type"] = "error"
        response["traceback"] = traceback.format_exc()
        response["message"] = str(e)
        response["status_code"] = 500
    finally:
        # send result to redis
        r.set(os.getenv("job_id"), json.dumps(response))
        r.expire(os.getenv("job_id"), 60)


def compose_code(code: str, test: str, state: dict) -> str:
    code += f"""
from dropbase.helpers.utils import _dict_from_pydantic_model

# initialize context
context = _dict_from_pydantic_model(Context)
context = Context(**context)

# initialize state
state = State(**{state})
"""
    code += test
    return code


def assign_last_expression(code: str) -> str:
    """
    get test code and assign last expression to a variable named result
    """
    module = ast.parse(code)

    if module.body:
        # get the last statement
        last_statement = module.body[-1]

        # Replace Expr statement with assignment to "result"
        assign = ast.Assign(targets=[ast.Name(id="result", ctx=ast.Store())], value=last_statement.value)
        module.body[-1] = assign

    # Transform the AST back to Python code
    return astor.to_source(module)
