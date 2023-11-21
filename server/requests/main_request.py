from requests import Session

from server.constants import DROPBASE_API_URL

base_url = DROPBASE_API_URL + "/worker/"


class DropbaseSession(Session):
    base_url = None

    def __init__(self, base_url=None):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        url = self.base_url + url
        return super().request(method, url, *args, **kwargs)


# class DropbaseSession(Session):
#     def __init__(self, base_url=None, access_token_header=None, refresh_token_header=None):
#         super().__init__()
#         self.base_url = base_url
#         self.access_token_header = access_token_header
#         self.refresh_token_header = refresh_token_header

#     def request(self, method, url, *args, **kwargs):
#         url = self.base_url + url
#         if self.access_token_header:
#             self.headers.update({self.access_token_header: kwargs.pop("access_token")})
#         if self.refresh_token_header:
#             self.headers.update({self.refresh_token_header: kwargs.pop("refresh_token")})
#         return super().request(method, url, *args, **kwargs)

session = DropbaseSession(base_url=base_url)
