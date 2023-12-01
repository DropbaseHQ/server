import importlib
import os
import sys
import traceback
from io import StringIO
from multiprocessing import Pipe, Process

from server.constants import cwd

# NOTE: do not delete these, referenecd by run_task
from server.controllers.run_sql import run_sql_from_string  # noqa


def run_process_function(function_name: str, args: dict):
    """
    for functions that are used by end developer and called from studio
    """
    # TODO: rename to run sql from srting
    parent_conn, child_conn = Pipe()
    task = Process(
        target=run_function,
        args=(child_conn, function_name, args),
    )
    task.start()
    task.join()
    success, stdout, result = parent_conn.recv()
    return {"success": success, "result": result, "stdout": stdout}


def run_function(child_conn, function_name, args):
    # Change the current working directory to root_directory
    os.chdir(cwd)
    sys.path.append(cwd)  # Append your root directory to the Python import path

    importlib.invalidate_caches()

    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        output = globals()[function_name](**args)
        child_logs = redirected_output.getvalue()
        child_conn.send((True, child_logs, output))
    except Exception:
        child_logs = redirected_output.getvalue()  # get print statements before exception
        exception = traceback.format_exc()  # get full exception traceback string
        child_conn.send((False, child_logs, exception))
    finally:
        child_conn.close()
        sys.stdout = old_stdout
