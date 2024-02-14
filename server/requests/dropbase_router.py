import logging
import json
from requests import Response
from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from server.constants import DROPBASE_API_URL, DROPBASE_TOKEN

from .main_request import DropbaseSession
from .misc import MiscRouter
from .app import AppRouter
from .page import PageRouter
from .auth import AuthRouter

base_url = DROPBASE_API_URL + "/worker/"

logger = logging.getLogger(__name__)


class DropbaseRouter:
    # TODO: review this. might not need a router class for just one call
    def __init__(self, access_token: str):
        self.session = DropbaseSession(base_url=base_url)

        if not access_token:
            raise Exception("No server access token found!")

        self.session.headers["Authorization"] = f"Bearer {access_token}"
        self.session.hooks["response"].append(self._response_interceptor)

        if not DROPBASE_TOKEN:
            raise Exception("No dropbase token found!")

        self.session.headers["dropbase-token"] = DROPBASE_TOKEN
        self._assign_sub_routers()

    def _assign_sub_routers(self):
        self.misc = MiscRouter(session=self.session)
        self.app = AppRouter(session=self.session)
        self.page = PageRouter(session=self.session)
        self.auth = AuthRouter(session=self.session)

    def _response_interceptor(self, response: Response, *args, **kwargs):
        if response.status_code == 401:
            logger.warning(
                f"Unable to authorize with server. Details: {response.json()}"
            )


def get_server_access_header(request: Request):
    if not "access-token" in request.headers:
        raise Exception("No server access token found")
    access_token_header = request.headers.get("access-token")
    return access_token_header


def get_dropbase_router(request: Request):
    if "access-token" in request.headers:
        access_token_header = request.headers.get("access-token")
    if not access_token_header:
        raise Exception("No server access token found")
    return DropbaseRouter(
        access_token=access_token_header,
    )
