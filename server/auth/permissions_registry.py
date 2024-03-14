import time
from uuid import UUID

from server.constants import CUSTOM_PERMISSIONS_EXPIRY_TIME

PERMISSISONS_EXPIRY_TIME = int(CUSTOM_PERMISSIONS_EXPIRY_TIME)


class RegistryResources:
    WORKSPACE = "workspaces"
    APP = "apps"


class PermissionsRegistry:
    def __init__(self):
        self._registry = {}

    def __iter__(self):
        return iter(self._registry.values())

    def _check_workspace_expiry(self, user_id: UUID, workspace_id: UUID):
        if (
            self._registry[user_id][RegistryResources.WORKSPACE][workspace_id][
                "expiry_time"
            ]
            < time.time()
        ):
            del self._registry[user_id][RegistryResources.WORKSPACE][workspace_id]
            return False
        return True

    def _check_app_expiry(self, user_id: UUID, app_id: UUID):
        if (
            self._registry[user_id][RegistryResources.APP][app_id]["expiry_time"]
            < time.time()
        ):
            del self._registry[user_id]["apps"][app_id]
            return False
        return True

    def save_workspace_permissions(
        self, user_id: UUID, workspace_id: UUID, permissions: list
    ):
        if user_id not in self._registry:
            self._registry[user_id] = {
                RegistryResources.WORKSPACE: {},
                RegistryResources.APP: {},
            }

        workspace_dict_path = self._registry[user_id][RegistryResources.WORKSPACE]

        if workspace_id not in workspace_dict_path:
            workspace_dict_path[workspace_id] = {}

        workspace_dict_path[workspace_id] = {
            "permissions": permissions,
            "expiry_time": time.time() + PERMISSISONS_EXPIRY_TIME,
        }

    def save_app_permissions(self, user_id: UUID, app_id: UUID, permissions: list):
        if user_id not in self._registry:
            self._registry[user_id] = {
                RegistryResources.WORKSPACE: {},
                RegistryResources.APP: {},
            }
        app_dict_path = self._registry[user_id][RegistryResources.APP]
        if app_id not in app_dict_path:
            app_dict_path[app_id] = {}

        app_dict_path[app_id] = {
            "permissions": permissions,
            "expiry_time": time.time() + PERMISSISONS_EXPIRY_TIME,
        }

    def get_user_workspace_permissions(self, user_id: UUID, workspace_id: UUID):
        if user_id not in self._registry:
            return {}
        if workspace_id not in self._registry[user_id][RegistryResources.WORKSPACE]:
            return {}
        if not self._check_workspace_expiry(user_id, workspace_id):
            return {}
        return (
            self._registry.get(user_id)
            .get(RegistryResources.WORKSPACE)
            .get(workspace_id)
            .get("permissions")
        )

    def get_user_app_permissions(self, user_id: UUID, app_id: UUID):
        if user_id not in self._registry:
            return {}
        if app_id not in self._registry[user_id][RegistryResources.APP]:
            return {}
        if not self._check_app_expiry(user_id, app_id):
            return {}
        return (
            self._registry.get(user_id)
            .get(RegistryResources.APP)
            .get(app_id)
            .get("permissions")
        )


permissions_registry = PermissionsRegistry()
