from .main_request import DropbaseSession
from .app import AppRouter
from .components import ComponentRouter
from .file import FileRouter
from .misc import MiscRouter
from .table import TableRouter
from .widget import WidgetRouter
from .sync import SyncRouter

from server.constants import DROPBASE_API_URL
from fastapi import Request
from pydantic import BaseModel

base_url = DROPBASE_API_URL + "/worker/"


class DropbaseRouter:
    def __init__(self, cookies):
        self.session = DropbaseSession(base_url=base_url)
        if type(cookies) == dict:
            self.cookies = cookies
        elif type(cookies) == AccessCookies:
            self.cookies = cookies.dict()
        self.session.cookies["access_token_cookie"] = self.cookies[
            "access_token_cookie"
        ]
        if "refresh_token_cookie" in self.cookies:
            self.session.cookies["refresh_token_cookie"] = self.cookies[
                "refresh_token_cookie"
            ]
        self._assign_sub_routers()

    def _assign_sub_routers(self):
        self.app = AppRouter(session=self.session)
        self.file = FileRouter(session=self.session)
        self.table = TableRouter(session=self.session)
        self.widget = WidgetRouter(session=self.session)
        self.component = ComponentRouter(session=self.session)
        self.misc = MiscRouter(session=self.session)
        self.sync = SyncRouter(session=self.session)


class AccessCookies(BaseModel):
    access_token_cookie: str
    refresh_token_cookie: str


def get_access_cookies(request: Request):
    access_token_header = request.cookies.get("access_token_cookie")
    if not access_token_header and "access-token" in request.headers:
        access_token_header = request.headers.get("access-token")
    # refresh_token_header = request.cookies.get("refresh_token_cookie")
    return AccessCookies(
        access_token_cookie=access_token_header,
        # refresh_token_cookie=refresh_token_header,
    )


def get_dropbase_router(request: Request):
    access_token_header = request.cookies.get("access_token_cookie")
    if not access_token_header and "access-token" in request.headers:
        access_token_header = request.headers.get("access-token")
    if not access_token_header:
        raise Exception("No access token found")
    print("access_token_header", access_token_header)
    return DropbaseRouter(
        cookies={
            "access_token_cookie": access_token_header,
        }
    )
