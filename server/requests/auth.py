import json
from cachetools import cached, TTLCache
from fastapi import HTTPException
from cachetools.keys import hashkey
from server.constants import CUSTOM_PERMISSIONS_EXPIRY_TIME
from .main_request import DropbaseSession

cache = TTLCache(maxsize=1024, ttl=CUSTOM_PERMISSIONS_EXPIRY_TIME)


def mykey(self, app_ids: str):
    jsonified_app_ids = json.dumps(app_ids)
    try:
        auth_token = self.session.headers.get("Authorization")
        hash = hashkey(jsonified_app_ids, auth_token)
        return hash
    except Exception:
        raise HTTPException(
            status_code=400, detail="Unable to hash check apps permissions."
        )


class AuthRouter:
    def __init__(self, session: DropbaseSession):
        self.session = session

    def verify_identity_token(self, access_token: str):
        return self.session.post(
            "verify_token",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    @cached(cache=cache, key=mykey)
    def check_apps_permissions(self, app_ids: str):
        return self.session.post(
            "check_apps_permissions",
            json={"app_ids": app_ids},
        )
