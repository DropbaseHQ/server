from server.requests.main_request import session


def get_app(app_id: str):
    return session.get(url=f"app/{app_id}")


def update_app(app_id: str, update_data: dict):
    return session.put(url=f"app/{app_id}", json=update_data)


def rename_app(rename_data: dict):
    return session.put(url="app/rename", json=rename_data)


def delete_app(app_id: str):
    return session.delete(url=f"app/{app_id}")
