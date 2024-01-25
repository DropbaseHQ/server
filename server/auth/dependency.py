import logging
import requests
import asyncio
from server.constants import DROPBASE_API_URL
from server.requests.dropbase_router import get_access_cookies, AccessCookies
from server.auth.permissions_registry import permissions_registry
from fastapi import Depends, Request, Response, HTTPException
from fastapi_jwt_auth import AuthJWT, exceptions
from pydantic import BaseModel

logger = logging.getLogger(__name__)

WORKER_SL_TOKEN_NAME = "worker_sl_token"


class Settings(BaseModel):
    authjwt_secret_key: str = "dropbase"
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_access_token_expires: int = 60 * 10  # 10 minutes


@AuthJWT.load_config
def get_config():
    return Settings()


def verify_server_token(cookies: AccessCookies):
    response = requests.post(
        DROPBASE_API_URL + "/worker/verify_token",
        cookies={"access_token_cookie": cookies.access_token_cookie},
    )
    if response.status_code != 200:
        raise Exception("Invalid server token")
    return response


def verify_user_access_token(request: Request, Authorize: AuthJWT):
    if not request.cookies.get("worker_sl_token"):
        server_access_cookies = get_access_cookies(request)
        logger.info("VERIFYING SERVER TOKEN")
        verify_response = requests.post(
            DROPBASE_API_URL + "/worker/verify_token",
            cookies={"access_token_cookie": server_access_cookies.access_token_cookie},
        )
        if verify_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid access token")
        worker_sl_token = Authorize.create_access_token(
            subject=verify_response.json().get("user_id")
        )
        max_age = 60
        raise HTTPException(
            status_code=303,
            detail="Invalid access token",
            headers={
                "set-cookie": f"{WORKER_SL_TOKEN_NAME}={worker_sl_token}; Max-Age={max_age}; Path=/; HttpOnly;"
            },
        )
    else:
        try:
            Authorize._access_cookie_key = WORKER_SL_TOKEN_NAME
            Authorize._verify_and_get_jwt_in_cookies("access", Authorize._request)
            subject = Authorize.get_jwt_subject()
            return subject
        except exceptions.JWTDecodeError:
            raise Exception("Invalid access token")


def get_resource_id_from_req_body(resource_id_accessor: str, request: Request):
    if request.headers.get("content-type") == "application/json":
        body = asyncio.run(request.json())
        return body.get(resource_id_accessor)
    return None


def check_user_app_permissions(
    request: Request,
    access_cookies: AccessCookies = Depends(get_access_cookies),
    Authorize: AuthJWT = Depends(),
):
    verify_response = verify_user_access_token(request, Authorize)
    if verify_response:
        user_id = verify_response
    if user_id is None:
        raise Exception("No user id provided")

    app_name = request.path_params.get("app_name")
    if app_name is None:
        app_name = get_resource_id_from_req_body("app_name", request)
    if app_name is None:
        raise Exception("No app name provided")

    workspace_id = request.headers.get("workspace-id")
    if not workspace_id:
        raise Exception("No workspace id provided")

    user_app_permissions = permissions_registry.get_user_app_permissions(
        app_name, user_id
    )

    if not user_app_permissions:
        logger.info("FETCHING PERMISSIONS FROM DROPBASE API")
        response = requests.post(
            DROPBASE_API_URL + f"/user/check_permission",
            cookies={"access_token_cookie": access_cookies.access_token_cookie},
            json={"workspace_id": workspace_id, "app_name": app_name},
        )
        if response.status_code != 200:
            raise Exception("Invalid access token")

        permissions_registry.save_permissions(app_name, user_id, response.json())

    user_app_permissions = permissions_registry.get_user_app_permissions(
        app_name, user_id
    )
    return user_app_permissions


class EnforceUserAppPermissions:
    def __init__(self, action: str):
        self.action = action

    def __call__(
        self, user_app_permissions: dict = Depends(check_user_app_permissions)
    ):
        print("allowed to perform action", user_app_permissions.get(self.action))
        if self.action not in user_app_permissions or not user_app_permissions.get(
            self.action
        ):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )

        return True
