from importlib.util import find_spec
from fastapi import Depends


def get_permission_dependency(action: str, resource: str):
    if find_spec("server.auth2") is None:
        return None
    from server.auth.dependency import CheckUserPermissions

    return Depends(CheckUserPermissions(action=action, resource=resource))


def get_permission_dependency_array(action: str, resource: str):
    dep = get_permission_dependency(action, resource)
    if find_spec("server.auth2") is None:
        return None
    return [dep]
