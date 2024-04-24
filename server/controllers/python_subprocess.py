# TODO: DELETE ME IS SQL IS NOT RUNNIGN FROM SERVER
import importlib
import os
import sys
from multiprocessing import Pipe, Process

from dropbase.helpers.utils import get_state
from server.constants import TASK_TIMEOUT, cwd


def verify_state(app_name: str, page_name: str, state: dict) -> bool:
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
    try:
        # Change the current working directory to root_directory
        os.chdir(cwd)
        importlib.invalidate_caches()
        sys.path.insert(0, cwd)
        get_state(app_name, page_name, state)
        child_conn.send(True)
    except Exception:
        child_conn.send(False)
    finally:
        child_conn.close()
