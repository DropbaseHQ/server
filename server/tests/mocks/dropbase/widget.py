from server.tests.mocks.util import mock_response


def create_widget_response(page_id: str, name: str, property: str, depends_on: str = None):
    return mock_response(json=None)


def update_widget_response(widget_id: str, update_data: dict):
    return mock_response(json=None)


def delete_widget_response(widget_id: str):
    return mock_response(json=None)
