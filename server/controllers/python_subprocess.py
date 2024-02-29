# TODO: revisit. only used to validate state
import importlib
import os
import sys

from server.constants import TASK_TIMEOUT, cwd
from server.controllers.state import verify_state


def verify_state_in_subprocess(child_conn, app_name, page_name, state):
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
