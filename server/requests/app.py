class AppRouter:
    def __init__(self, session):
        self.session = session

    def create_app(self, app_properties: dict):
        return self.session.post(
            url="app/",
            json={**app_properties},
        )
