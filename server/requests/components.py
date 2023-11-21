from server.requests.main_request import session


def create_component(payload: dict):
    return session.post(url="components/", json=payload)


def update_component(component_id: str, update_data: dict):
    return session.put(url=f"components/{component_id}", json=update_data)


def delete_component(component_id: str):
    return session.delete(url=f"components/{component_id}")
