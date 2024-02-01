from uuid import UUID
import time


PERMISSISONS_EXPIRY_TIME = 60  # 1 minute


class PermissionsRegistry:
    def __init__(self):
        self._registry = {}

    def __iter__(self):
        return iter(self._registry.values())

    def _check_expiry(self, user_id: UUID, app_id: UUID):
        if self._registry[user_id][app_id]["expiry_time"] < time.time():
            print("EXPIRED")
            del self._registry[user_id][app_id]
            return False
        return True

    def save_permissions(self, user_id: UUID, app_id: UUID, permissions: list):
        if user_id not in self._registry:
            self._registry[user_id] = {}
        if app_id not in self._registry[user_id]:
            self._registry[user_id][app_id] = {}

        self._registry[user_id][app_id] = {
            "permissions": permissions,
            "expiry_time": time.time() + PERMISSISONS_EXPIRY_TIME,
        }

    def get_user_app_permissions(self, user_id: UUID, app_id: UUID):
        if user_id not in self._registry:
            return {}
        if app_id not in self._registry[user_id]:
            return {}
        if not self._check_expiry(user_id, app_id):
            return {}
        return self._registry.get(user_id).get(app_id).get("permissions")


permissions_registry = PermissionsRegistry()
