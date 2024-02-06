class AuthRouter:
    def __init__(self, session):
        self.session = session

    def verify_identity_token(self, access_token: str):
        return self.session.post(
            "verify_token",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def check_permissions(self, workspace_id: str, app_id: str, access_token: str):
        return self.session.post(
            "check_permission",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"workspace_id": workspace_id, "app_id": app_id},
        )
