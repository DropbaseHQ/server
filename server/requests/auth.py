import json
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from server.constants import CUSTOM_PERMISSIONS_EXPIRY_TIME


cache = TTLCache(maxsize=1024, ttl=CUSTOM_PERMISSIONS_EXPIRY_TIME)


def mykey(_, apps: str):
    apps = json.loads(apps)
    app_ids = [app.get("id") for app in apps]
    jsonified_app_ids = json.dumps(app_ids)

    hash = hashkey(jsonified_app_ids)

    return hash


class AuthRouter:
    def __init__(self, session):
        self.session = session

    def verify_identity_token(self, access_token: str):
        return self.session.post(
            "verify_token",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def check_permissions(self, app_id: str, access_token: str):
        return self.session.post(
            "check_permission",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"app_id": app_id},
        )

    @cached(cache=cache, key=mykey)
    def check_apps_permissions(self, apps: str):
        apps = json.loads(apps)
        print("getting permissions for apps")
        return self.session.post(
            "check_apps_permissions",
            json={"apps": apps},
        )

    def get_worker_workspace(self):
        return self.session.get("worker_workspace")
