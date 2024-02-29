import importlib
import os
import sys
from multiprocessing import Pipe, Process

from server.constants import TASK_TIMEOUT, cwd
from server.controllers.state import verify_state


def verify_state_in_subprocess(app_name, page_name, state):
    """
    for functions that are called internally by the controller,
    where we don't need the status_code output.

    throws exception instead.
    """
    parent_conn, child_conn = Pipe()

    task = Process(
        target=run_task,
        args=(child_conn, app_name, page_name, state),
    )

    task.start()
    task.join(timeout=int(TASK_TIMEOUT))

    if task.is_alive():
        task.terminate()
        task.join()  # Join again after terminating to cleanup resources
        return False

    success = parent_conn.recv()

    return success


def run_task(child_conn, app_name, page_name, state):
    # Change the current working directory to root_directory
    os.chdir(cwd)
    sys.path.append(cwd)  # Append your root directory to the Python import path

    importlib.invalidate_caches()

    try:
        status_code = verify_state(app_name, page_name, state)
        child_conn.send(status_code == 200)

    except Exception:
        child_conn.send(False)

    finally:
        child_conn.close()


def format_process_result(result: any, stdout: str = "", success: bool = True):
    return {"result": result, "stdout": stdout, "success": success}
