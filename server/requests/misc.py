class MiscRouter:
    def __init__(self, session):
        self.session = session

    def get_smart_columns(self, payload: dict):
        return self.session.post(url="get_smart_cols/", json=payload)
