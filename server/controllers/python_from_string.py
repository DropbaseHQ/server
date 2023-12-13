import ast
import importlib
import json
import os
import runpy
import sys
import tempfile
import traceback
from io import StringIO
from multiprocessing import Pipe, Process

import astor
import pandas as pd

from server.constants import DATA_PREVIEW_SIZE, TASK_TIMEOUT, cwd
from server.controllers.utils import clean_df, convert_df_to_resp_obj


def run_process_with_exec(args: dict):
    parent_conn, child_conn = Pipe()
    task = Process(
        target=run_exec_task,
        args=(child_conn, args),
    )
    task.start()
    task.join(timeout=int(TASK_TIMEOUT))

    if task.is_alive():
        task.terminate()
        task.join()  # Join again after terminating to cleanup resources
        return {
            "success": False,
            "result": None,
            "stdout": "Task did not complete within the timeout period, so it was terminated.",
        }

    success, stdout, result = parent_conn.recv()
    # task.terminate()
    return {"success": success, "result": result, "stdout": stdout}


def run_exec_task(child_conn, args):
    output = None
    # Change the current working directory to root_directory
    os.chdir(cwd)
    sys.path.append(cwd)  # Append your root directory to the Python import path

    importlib.invalidate_caches()

    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        code_block, last_expr = compose_string_to_exec(
            args.get("app_name"),
            args.get("page_name"),
            args.get("payload"),
            args.get("python_string"),
            args.get("file"),
        )

        with tempfile.NamedTemporaryFile(mode="wt", delete=True) as temp:
            temp.write(code_block)
            temp.flush()

            # Now run the script using runpy
            ns = runpy.run_path(temp.name)
            #  get the results
            variables = {k: v for k, v in ns.items() if not k.startswith("__")}

        globals_for_exec = {}
        locals_for_exec = variables.copy()

        # Return the result of the last node
        last_var = eval(
            compile(last_expr, filename="<ast>", mode="eval"), globals_for_exec, locals_for_exec
        )
        if type(last_var) is pd.DataFrame:
            last_var = clean_df(last_var)
            last_var = last_var[:DATA_PREVIEW_SIZE]
            # output = json.loads(last_var.to_json(orient="split"))
            output = convert_df_to_resp_obj(last_var)
        elif last_var.__class__.__name__ == "Context":
            output = {"context": last_var.dict()}
        else:
            output = last_var

        child_logs = redirected_output.getvalue()
        child_conn.send((True, child_logs, output))
    except Exception:
        child_logs = redirected_output.getvalue()  # get print statements before exception
        exception = traceback.format_exc()  # get full exception traceback string
        child_conn.send((False, child_logs, exception))
    finally:
        child_conn.close()
        sys.stdout = old_stdout


def compose_string_to_exec(app_name: str, page_name: str, payload: dict, python_string: str, file: dict):
    file_name = file.get("name") + ".sql" if file.get("type") == "sql" else file.get("name") + ".py"
    file_path = f"/workspace/{app_name}/{page_name}/scripts/{file_name}"
    file_content = ""
    with open(cwd + file_path, "r") as f:
        file_content = f.read()
    compose_run_python_str = file_content
    compose_run_python_str += f"""\n\n
from workspace.{app_name}.{page_name} import Context, State
from workspace.{app_name}.{page_name}.scripts import *

payload = {payload}

context = Context(**payload.get('context'))
state = State(**payload.get('state'))\n\n
"""

    tree = ast.parse(python_string, mode="exec")

    if len(tree.body) > 1:
        for node in tree.body[:-1]:
            compose_run_python_str += astor.to_source(node) + "\n\n"
    last_expr = ast.Expression(tree.body[-1].value)
    return compose_run_python_str, last_expr
