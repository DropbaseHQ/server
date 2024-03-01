import importlib
import os
import sys
from multiprocessing import Pipe, Process

from server.constants import TASK_TIMEOUT, cwd
from server.controllers.utils import get_state


def verify_state_subprocess(app_name, page_name, state) -> bool:
    parent_conn, child_conn = Pipe()
    task = Process(
        target=_run_task,
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


def _run_task(child_conn, app_name, page_name, state):
    # Change the current working directory to root_directory
    os.chdir(cwd)

    importlib.invalidate_caches()

    try:
        sys.path.insert(0, cwd)
        get_state(app_name, page_name, state)
        child_conn.send(True)

    except Exception:
        child_conn.send(False)

    finally:
        child_conn.close()


def format_process_result(result: any, stdout: str = "", success: bool = True):
    return {"result": result, "stdout": stdout, "success": success}
