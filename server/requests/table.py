from requests import Session


class TableRouter:
    def __init__(self, session: Session):
        self.session = session

    def create_table(self, page_id: str, name: str, property: str, depends_on: str):
        return self.session.post(
            url="table/",
            json={
                "name": name,
                "property": property,
                "page_id": page_id,
                "depends_on": depends_on,
            },
        )

    def update_table(self, table_id: str, update_data: dict):
        return self.session.put(url="table/", json=update_data)

    def update_table_property(self, table_id: str, update_data: dict):
        return self.session.put(url=f"table/properpy/{table_id}", json=update_data)

    def update_table_columns(self, table_id: str, update_data: dict):
        return self.session.put(url=f"table/columns/{table_id}", json=update_data)

    def delete_table(self, table_id: str):
        return self.session.delete(url=f"table/{table_id}/")
