import importlib
import os
import sys
import traceback
from io import StringIO
from multiprocessing import Pipe, Process

from server.constants import TASK_TIMEOUT, cwd

# NOTE: do not delete these, referenecd by run_task
from server.controllers.run_python import run_df_function, run_python_query, run_python_ui  # noqa
from server.controllers.state import verify_state  # noqa


def run_process_task_unwrap(*args, **kwargs):
    """
    for functions that are called internally by the controller,
    where we don't need the status_code output.

    throws exception instead.
    """
    resp, status_code = run_process_task(*args, **kwargs)
    if status_code == 200:
        return format_process_result(resp["result"])
    else:
        raise Exception(resp["result"])


def run_process_task(function_name: str, args: dict):
    """
    for functions that are called by ui and used by end user
    """
    parent_conn, child_conn = Pipe()
    task = Process(
        target=run_task,
        args=(child_conn, function_name, args),
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
        }, 500

    status_code, stdout, result = parent_conn.recv()
    # task.terminate()
    if status_code != 200:
        # for troubleshooting purposes
        print(stdout)
    return format_process_result(result, stdout), status_code


def run_task(child_conn, function_name, args):
    # Change the current working directory to root_directory
    os.chdir(cwd)
    sys.path.append(cwd)  # Append your root directory to the Python import path

    importlib.invalidate_caches()

    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        output, status_code = globals()[function_name](**args)
        child_logs = redirected_output.getvalue()
        child_conn.send((status_code, child_logs, output))
    except Exception:
        child_logs = redirected_output.getvalue()  # get print statements before exception
        exception = traceback.format_exc()  # get full exception traceback string
        child_conn.send((500, child_logs, exception))
    finally:
        child_conn.close()
        sys.stdout = old_stdout


def format_process_result(result: any, stdout: str = "", success: bool = True):
    return {"result": result, "stdout": stdout, "success": success}
