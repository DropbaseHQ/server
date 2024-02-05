# TODO: revisit. only used to validate state
import importlib
import os
import pickle
import sys
import traceback
import uuid
from io import StringIO
from multiprocessing import Pipe, Process

from server.constants import TASK_TIMEOUT, cwd

# NOTE: do not delete these, referenecd by run_task
from server.controllers.run_python import run_python_ui  # noqa
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

    status_code, stdout, file_path = parent_conn.recv()
    result = None
    try:
        # read results from file
        with open(file_path, "rb") as f:
            result = pickle.load(f)
    finally:
        # remove file
        os.remove(file_path)

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

    # random file name
    random_file_name = uuid.uuid4().hex
    file_path = cwd + f"/.temp/{random_file_name}.pkl"

    try:
        output, status_code = globals()[function_name](**args)
        # save output to file
        with open(file_path, "wb") as f:
            pickle.dump(output, f)

        child_logs = redirected_output.getvalue()
        child_conn.send((status_code, child_logs, file_path))
    except Exception:
        # save exception to file
        exception = traceback.format_exc()  # get full exception traceback string
        with open(file_path, "wb") as f:
            pickle.dump(exception, f)

        child_logs = redirected_output.getvalue()  # get print statements before exception
        child_conn.send((500, child_logs, file_path))
    finally:
        child_conn.close()
        sys.stdout = old_stdout


def format_process_result(result: any, stdout: str = "", success: bool = True):
    return {"result": result, "stdout": stdout, "success": success}
