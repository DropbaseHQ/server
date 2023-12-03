import sys

from server.constants import cwd
from server.controllers.utils import get_state


def verify_state(app_name: str, page_name: str, state: dict):
    """
    verifies state dict with the State object defined for a given app and page
    """
    try:
        sys.path.insert(0, cwd)
        get_state(app_name, page_name, state)
        return None, 200
    except Exception as e:
        return {"error": str(e)}, 500
