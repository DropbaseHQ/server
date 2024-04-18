from importlib.util import find_spec
from fastapi import Depends

auth_module_is_installed = find_spec("server.auth") is not None


def get_permission_dependency(action: str, resource: str):
    print("over here")
    if not auth_module_is_installed:
        return None
    from server.auth.authorization import AuthZDepFactory

    app_auth = AuthZDepFactory(default_resource_type="app")
    print("Here")
    response = Depends(app_auth.use_params(action=action, resource_type=resource))
    print("response", response)
    return Depends(app_auth.use_params(action=action, resource_type=resource))


def get_permission_dependency_array(action: str, resource: str):

    dep = get_permission_dependency(action, resource)
    if not auth_module_is_installed:
        return None
    return [dep]


def get_parsed_apps(apps):
    filtered_apps = filter_apps(db, apps, workspace_id, user_id)
    print("filtered_apps", filtered_apps)
    if not auth_module_is_installed:
        return apps
    from server.auth.controllers.app import filter_apps
