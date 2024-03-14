class MiscRouter:
    def __init__(self, session):
        self.session = session

    def sync_table_columns(self, payload: dict):
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

    def get_smart_columns(self, payload: dict):
        return self.session.post(url="get_smart_cols/", json=payload)

    def sync_demo(self):
        return self.session.get(url="sync_demo/")
