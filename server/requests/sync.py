class SyncRouter:
    def __init__(self, session):
        self.session = session

    def sync_columns(self, payload: dict):
        return self.session.post(url="sync/columns/", json=payload)

    def sync_components(self, app_name: str, page_name: str, token: str):
        return self.session.post(
            url="sync/components/",
            json={
                "app_name": app_name,
                "page_name": page_name,
                "token": token,
            },
        )

    def sync_page(self, page_id: str):
        return self.session.put(url=f"sync/page/{page_id}")
