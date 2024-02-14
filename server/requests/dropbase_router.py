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
    def __init__(self, cookies):
        self.session = DropbaseSession(base_url=base_url)

        if type(cookies) is dict:
            self.cookies = cookies

        elif type(cookies) is AccessCookies:
            self.cookies = cookies.dict()

        self.session.cookies["access_token_cookie"] = self.cookies[
            "access_token_cookie"
        ]
        if "refresh_token_cookie" in self.cookies:
            self.session.cookies["refresh_token_cookie"] = self.cookies[
                "refresh_token_cookie"
            ]

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


class AccessCookies(BaseModel):
    access_token_cookie: str
    refresh_token_cookie: Optional[str]


def get_access_cookies(request: Request):
    access_token_header = request.cookies.get("access_token_cookie")
    if not access_token_header and "access-token" in request.headers:
        access_token_header = request.headers.get("access-token")
    return AccessCookies(
        access_token_cookie=access_token_header,
    )


def get_dropbase_router(request: Request):
    access_token_header = request.cookies.get("access_token_cookie")
    if not access_token_header and "access-token" in request.headers:
        access_token_header = request.headers.get("access-token")
    if not access_token_header:
        raise Exception("No access token found")
    return DropbaseRouter(
        cookies={
            "access_token_cookie": access_token_header,
        }
    )
