class PageRouter:
    def __init__(self, session):
        self.session = session

    def create_page(self, page_properties: dict):
        return self.session.post(
            url="page/",
            json={**page_properties},
        )
