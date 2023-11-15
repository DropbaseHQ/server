from requests import Session


class AppRouter:
    def __init__(self, session: Session):
        self.session = session

    def get_app(self, app_id: str):
        return self.session.get(url=f"app/{app_id}")

    def rename_app(self, rename_data: dict):
        return self.session.put(url="app/rename", json=rename_data)

    def update_app(self, app_id: str, update_data: dict):
        return self.session.put(url=f"app/{app_id}", json=update_data)

    def delete_app(self, app_id: str):
        return self.session.delete(url=f"app/{app_id}")
