import ast
import json
import os
import traceback

import astor
import redis


def assign_last_expression(script: str) -> str:
    """
    get test code and assign last expression to a variable named result
    """
    module = ast.parse(script)

    if module.body:
        last_statement = module.body[-1]

        # Replace Expr statement with assignment to "_"
        assign = ast.Assign(targets=[ast.Name(id="result", ctx=ast.Store())], value=last_statement.value)
        module.body[-1] = assign

    # Transform the AST back to Python code
    return astor.to_source(module)


def write_file(file_code: str, test_code: str, state: dict, file_name: str):
    python_str = file_code
    python_str += f"""
import json

state = {state}

try:
    state = State(**state)
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
file_name = "temp.py"

try:
    file_code = os.getenv("file_code")
    state = json.loads(os.getenv("state"))
    test_code = os.getenv("test_code")

    # assign last expression to variable if needed
    test_code = assign_last_expression(test_code)

    # write exec file
    write_file(file_code, test_code, state, file_name)

    # import the file
    from temp import result

    # send result to redis
    r.set(job_id, result)
    r.expire(job_id, 60)

except Exception as e:
    error_string = traceback.format_exc()
    result = error_string + str(e)
    r.set(job_id, result)
    r.expire(job_id, 60)
