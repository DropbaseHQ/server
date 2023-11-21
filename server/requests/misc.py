class MiscRouter:
    def __init__(self, session):
        self.session = session

    def sync_table_columns(
        self,
        app_name: str,
        page_name: str,
        table_columns: dict,
        token: str,
        table_type: str,
    ):
        return self.session.post(
            url="sync/columns/",
            json={
                "app_name": app_name,
                "page_name": page_name,
                "table_columns": table_columns,
                "token": token,
                "table_type": table_type,
            },
        )

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

    def update_smart_columns(self, payload: dict):
        return self.session.post(url="update_smart_cols/", json=payload)
