import asyncio
import logging
import os
import jwt

import requests
from fastapi import Depends, HTTPException, Request
from fastapi_jwt_auth import AuthJWT, exceptions
from pydantic import BaseModel

from server.auth.permissions_registry import permissions_registry
from server.constants import DROPBASE_API_URL
from server.requests.dropbase_router import AccessCookies, get_access_cookies
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.controllers.workspace import WorkspaceFolderController


cwd = os.getcwd()
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


def verify_server_access_token(
    access_token, Authorize: AuthJWT, router: DropbaseRouter
):
    logger.info("VERIFYING SERVER TOKEN")
    verify_response = router.auth.verify_identity_token(access_token)
    if verify_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid access token")
    worker_sl_token = Authorize.create_access_token(
        subject=verify_response.json().get("user_id")
    )
    max_age = 60 * 5
    raise HTTPException(
        status_code=401,
        detail="Invalid access token",
        headers={
            "set-cookie": f"{WORKER_SL_TOKEN_NAME}={worker_sl_token}; Max-Age={max_age}; Path=/;"  # noqa
        },
    )


def verify_user_access_token(
    request: Request, Authorize: AuthJWT, router: DropbaseRouter
):
    server_access_cookies = get_access_cookies(request)

    if not request.cookies.get("worker_sl_token"):
        verify_server_access_token(
            access_token=server_access_cookies.access_token_cookie,
            Authorize=Authorize,
            router=router,
        )
    else:
        try:
            Authorize._access_cookie_key = WORKER_SL_TOKEN_NAME
            Authorize._verify_and_get_jwt_in_cookies("access", Authorize._request)
            worker_subject = Authorize.get_jwt_subject()

            server_claims = jwt.decode(
                server_access_cookies.access_token_cookie, verify=False
            )

            if worker_subject != server_claims.get("user_id"):
                verify_server_access_token(
                    access_token=server_access_cookies.access_token_cookie,
                    Authorize=Authorize,
                    router=router,
                )
            return worker_subject
        except exceptions.JWTDecodeError:
            raise Exception("Invalid access token")


def get_resource_id_from_req_body(resource_id_accessor: str, request: Request):
    if request.headers.get("content-type") == "application/json":
        body = asyncio.run(request.json())
        return body.get(resource_id_accessor)
    return None


class CheckUserPermissions:
    APP = "app"
    WORKSPACE = "workspace"

    def __init__(self, action=str, resource: str = None):
        self.action = action
        self.resource = resource

    def _get_app_id(self, request: Request):
        app_name = request.path_params.get("app_name")
        if app_name is None:
            app_name = get_resource_id_from_req_body("app_name", request)
        if app_name is None:
            raise Exception("No app name provided")

        workspace_folder_controller = WorkspaceFolderController(
            r_path_to_workspace=os.path.join(cwd, "workspace")
        )
        app_id = workspace_folder_controller.get_app_id(app_name=app_name)
        if app_id is None:
            raise Exception(f"App {app_name} either does not exist or has no id.")
        return app_id

    def _get_resource_permissions(
        self, request: Request, user_id: str, workspace_id: str
    ):
        if self.resource == self.WORKSPACE:
            return permissions_registry.get_user_workspace_permissions(
                user_id=user_id, workspace_id=workspace_id
            )
        elif self.resource == self.APP:
            app_id = self._get_app_id(request)
            return permissions_registry.get_user_app_permissions(
                user_id=user_id, app_id=app_id
            )
        else:
            raise Exception("No resource provided")

    def _load_fresh_permissions(
        self,
        access_cookies: AccessCookies,
        workspace_id: str,
        user_id: str,
        app_id: str = None,
    ):
        logger.info("FETCHING PERMISSIONS FROM DROPBASE API")
        payload = {"workspace_id": workspace_id}
        if app_id:
            payload["app_id"] = app_id

        response = requests.post(
            DROPBASE_API_URL + "/user/check_permission",
            headers={"Authorization": f"Bearer {access_cookies.access_token_cookie}"},
            json=payload,
        )

        if response.status_code == 401:
            logger.warning(
                "Dropbase Token: ", router.session.headers.get("dropbase-token")
            )
            logger.warning("Request headers", response.request.headers)
            logger.warning("Invalid access token", response.text)
            raise Exception("Invalid access token")
        workspace_permissions = response.json().get("workspace_permissions")
        app_permissions = response.json().get("app_permissions")

        permissions_registry.save_workspace_permissions(
            user_id=user_id,
            workspace_id=workspace_id,
            permissions=workspace_permissions,
        )
        permissions_registry.save_app_permissions(
            app_id=app_id, user_id=user_id, permissions=app_permissions
        )

    def _get_permissions(self, request: Request, user_id: str, workspace_id: str):
        if self.resource == self.WORKSPACE:
            user_permissions = permissions_registry.get_user_workspace_permissions(
                user_id=user_id, workspace_id=workspace_id
            )
        elif self.resource == self.APP:
            app_id = self._get_app_id(request)
            user_permissions = permissions_registry.get_user_app_permissions(
                user_id=user_id, app_id=app_id
            )

        return user_permissions

    def __call__(
        self,
        request: Request,
        access_cookies: AccessCookies = Depends(get_access_cookies),
        Authorize: AuthJWT = Depends(),
    ):
        verify_response = verify_user_access_token(request, Authorize)
        if verify_response:
            user_id = verify_response
        if user_id is None:
            raise Exception("No user id provided")

        workspace_id = request.headers.get("workspace-id")
        if not workspace_id:
            raise Exception("No workspace id provided")

        if self.resource is None:
            logger.warning("No resource provided. Workspace assumed.")
            self.resource = "workspace"

        user_permissions = self._get_resource_permissions(
            request=request, user_id=user_id, workspace_id=workspace_id
        )

        app_id = self._get_app_id(request)
        if not user_permissions:
            self._load_fresh_permissions(
                access_cookies=access_cookies,
                workspace_id=workspace_id,
                user_id=user_id,
                app_id=app_id,
            )
        final_user_permissions = self._get_permissions(
            request=request, user_id=user_id, workspace_id=workspace_id
        )

        if self.action not in final_user_permissions or not final_user_permissions.get(
            self.action
        ):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )

        return final_user_permissions

    # The below two methods are used for testing purposes
    # Since this class is a dependency, we need to override it when testing
    # However, since it is not a function, but a class with which we pass arguments to,
    # it will not work with the dependency_overrides parameter in the test client.
    # The dependency needs to be hashable to be recognized properly by dependency_overrides.
    # This is why we have to override the __hash__ and __eq__ methods.

    # Solution from: https://github.com/tiangolo/fastapi/discussions/6834
    def __hash__(self):
        # FIXME find something uniq and repeatable
        return 1234

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, CheckUserPermissions):

            return self.action == other.action and self.resource == other.resource
        return False
