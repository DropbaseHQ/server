from importlib.util import find_spec
from fastapi import Depends

auth_module_is_installed = find_spec("server.auth") is not None


def get_permission_dependency(action: str, resource: str):
    if not auth_module_is_installed:
        return None
    from server.auth.authorization import AuthZDepFactory

    app_auth = AuthZDepFactory(default_resource_type="app")
    return Depends(app_auth.use_params(action=action, resource_type=resource))


def get_permission_dependency_array(action: str, resource: str):

    dep = get_permission_dependency(action, resource)
    if not auth_module_is_installed:
        return None
    return [dep]
