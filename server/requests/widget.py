from server.requests.main_request import session


def create_widget(page_id: str, name: str, property: str, depends_on: str = None):
    return session.post(
        url="widget/",
        json={"name": name, "property": property, "page_id": page_id, "depends_on": depends_on},
    )


def update_widget(widget_id: str, update_data: dict):
    return session.put(url=f"widget/{widget_id}", json=update_data)


def delete_widget(widget_id: str):
    return session.delete(url=f"widget/{widget_id}")
