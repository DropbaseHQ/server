from requests import Session


class FileRouter:
    def __init__(self, session: Session):
        self.session = session

    def get_file(self, file_id: str):
        return self.session.get(url=f"files/{file_id}")

    def create_file(self, payload: dict):
        return self.session.post(url="files/", json=payload)

    def update_file(self, file_id: str, update_data: dict):
        return self.session.put(url=f"files/{file_id}", json=update_data)

    def update_file_name(self, update_data: dict):
        return self.session.put(url="files/rename", json=update_data)

    def delete_file(self, file_id: str):
        return self.session.delete(url=f"files/{file_id}")
