class PageRouter:
    def __init__(self, session):
        self.session = session

    def create_page(self, page_properties: dict):
        return self.session.post(
            url="page/",
            json={**page_properties},
        )

    def delete_page(self, page_id: str):
        return self.session.delete(url=f"page/{page_id}")
