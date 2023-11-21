from server.requests.main_request import session


def get_smart_columns(payload: dict):
    return session.post(url="get_smart_cols/", json=payload)


def update_smart_columns(payload: dict):
    return session.post(url="update_smart_cols/", json=payload)
