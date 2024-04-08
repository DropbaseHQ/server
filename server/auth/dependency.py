import asyncio
import logging
import os

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi_jwt_auth import AuthJWT, exceptions
from pydantic import BaseModel

from server.auth.permissions_registry import permissions_registry
from server.controllers.workspace import WorkspaceFolderController
from server.requests.dropbase_router import (
    DropbaseRouter,
    get_dropbase_router,
    get_server_access_header,
)

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
        detail="Issuing new worker token. Please try again.",
        headers={
            "set-cookie": f"{WORKER_SL_TOKEN_NAME}={worker_sl_token}; Max-Age={max_age}; Path=/;"  # noqa
        },
    )


def verify_worker_access_token(
    request: Request, Authorize: AuthJWT, router: DropbaseRouter
):
    access_token = get_server_access_header(request)

    if not request.cookies.get("worker_sl_token"):
        verify_server_access_token(
            access_token=access_token,
            Authorize=Authorize,
            router=router,
        )
    else:
        try:
            Authorize._access_cookie_key = WORKER_SL_TOKEN_NAME
            Authorize._verify_and_get_jwt_in_cookies("access", Authorize._request)
            worker_subject = Authorize.get_jwt_subject()

            server_claims = jwt.decode(access_token, verify=False)

            if worker_subject != server_claims.get("user_id"):
                verify_server_access_token(
                    access_token=access_token,
                    Authorize=Authorize,
                    router=router,
                )
            return worker_subject
        except exceptions.JWTDecodeError:
            raise HTTPException(
                status_code=401,
                detail="Worker token was found, but not able to be validated",
            )


def get_resource_id_from_req_body(resource_id_accessor: str, request: Request):
    if request.headers.get("content-type") == "application/json":
        body = asyncio.run(request.json())
        return body.get(resource_id_accessor)
    return None
