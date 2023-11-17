from server.requests.main_request import session


def create_table(page_id: str, name: str, property: str, depends_on: str):
    return session.post(
        url="table/",
        json={
            "name": name,
            "property": property,
            "page_id": page_id,
            "depends_on": depends_on,
        },
    )


def update_table(table_id: str, update_data: dict):
    return session.put(url="table/", json=update_data)


def update_table_property(table_id: str, update_data: dict):
    return session.put(url=f"table/properpy/{table_id}/", json=update_data)


def update_table_columns(table_id: str, update_data: dict):
    return session.put(url=f"table/columns/{table_id}/", json=update_data)


def delete_table(table_id: str):
    return session.delete(url=f"table/{table_id}/")
