from requests import Session

from server.constants import DROPBASE_API_URL

base_url = DROPBASE_API_URL + "/worker/"


class DropbaseSession(Session):
    def __init__(self, base_url=None):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        url = self.base_url + url
        return super().request(method, url, *args, **kwargs)


session = DropbaseSession(base_url=base_url)
