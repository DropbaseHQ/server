from server.requests.main_request import session


def sync_columns(payload: dict):
    return session.post(url="sync/columns/", json=payload)


def sync_components(app_name: str, page_name: str, token: str):
    return session.post(
        url="sync/components/",
        json={
            "app_name": app_name,
            "page_name": page_name,
            "token": token,
        },
    )


def sync_page(page_id: str):
    return session.put(url=f"sync/page/{page_id}")
