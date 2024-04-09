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


def get_resource_id_from_req_body(resource_id_accessor: str, request: Request):
    if request.headers.get("content-type") == "application/json":
        body = asyncio.run(request.json())
        return body.get(resource_id_accessor)
    return None
