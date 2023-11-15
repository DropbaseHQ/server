from .main_request import DropbaseSession
from .app import AppRouter
from .components import ComponentRouter
from .file import FileRouter
from .misc import MiscRouter
from .table import TableRouter
from .widget import WidgetRouter

from server.constants import DROPBASE_API_URL
from fastapi import Request

base_url = DROPBASE_API_URL + "/worker/"


class DropbaseRouter:
    def __init__(self, cookies):
        self.session = DropbaseSession(base_url=base_url)
        self.cookies = cookies
        self.session.cookies["access_token_cookie"] = cookies["access_token_cookie"]
        self.session.cookies["refresh_token_cookie"] = cookies["refresh_token_cookie"]
        self._assign_sub_routers()

    def _assign_sub_routers(self):
        self.app = AppRouter(session=self.session)
        self.file = FileRouter(session=self.session)
        self.table = TableRouter(session=self.session)
        self.widget = WidgetRouter(session=self.session)
        self.component = ComponentRouter(session=self.session)
        self.misc = MiscRouter(session=self.session)


def get_dropbase_router(request: Request):
    access_token_header = request.cookies.get("access_token_cookie")
    refresh_token_header = request.cookies.get("refresh_token_cookie")
    return DropbaseRouter(
        cookies={
            "access_token_cookie": access_token_header,
            "refresh_token_cookie": refresh_token_header,
        }
    )
