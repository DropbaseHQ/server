from server.tests.mocks.util import mock_response


def update_table_property_response(table_id: str, update_data: dict, depends_on=None):
    return mock_response(
        json={
            "name": update_data["name"],
            "property": update_data["property"],
            "page_id": update_data["page_id"],
            "date": "2023-11-07T22:14:14.844164",
            "file_id": update_data["file_id"],
            "id": table_id,
            "depends_on": depends_on,
        }
    )
