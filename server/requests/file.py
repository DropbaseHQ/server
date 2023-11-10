from server.requests.main_request import session


def get_file(file_id: str):
    return session.get(url=f"files/{file_id}")


def create_file(payload: dict):
    return session.post(url="files/", json=payload)


def update_file(file_id: str, update_data: dict):
    return session.put(url=f"files/{file_id}", json=update_data)


def update_file_name(update_data: dict):
    return session.put(url="files/rename", json=update_data)


def delete_file(file_id: str):
    return session.delete(url=f"files/{file_id}")
