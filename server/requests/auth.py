class AuthRouter:
    def __init__(self, session):
        self.session = session

    def verify_identity_token(self, access_token: str):
        return self.session.post(
            "verify_token",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def check_permissions(self, app_id: str, access_token: str):
        return self.session.post(
            "check_permission",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"app_id": app_id},
        )

    def get_worker_workspace(self):
        return self.session.get("worker_workspace")
