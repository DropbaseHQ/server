from server.tests.mocks.util import mock_response


def get_app_response(name="dropbase_test_app"):
    return lambda app_id: mock_response(
        json={
            "date": "2023-10-31T14:22:45.654115",
            "name": name,
            "workspace_id": "be5a519f-b9df-4f09-9f10-ce2f18d9a5ca",
            "is_draft": False,
            "id": app_id,
        }
    )


def update_app_response(app_id: str, update_data: dict):
    return mock_response(
        json={
            "date": "2023-10-31T14:22:45.654115",
            "name": update_data.get("name", "dropbase_test_app"),
            "workspace_id": "be5a519f-b9df-4f09-9f10-ce2f18d9a5ca",
            "is_draft": False,
            "id": app_id,
        }
    )


def rename_app_response(*args, **kwargs):
    # not implemented
    return mock_response(json={})


def delete_app_response(app_id: str):
    return mock_response(
        json={
            "date": "2023-10-31T14:22:45.654115",
            "name": "dropbase_test_app",
            "workspace_id": "be5a519f-b9df-4f09-9f10-ce2f18d9a5ca",
            "is_draft": False,
            "id": app_id,
        }
    )


def delete_app_response_path_traversal(app_name: str):
    return lambda app_id: mock_response(
        json={
            "date": "2023-10-31T14:22:45.654115",
            "name": app_name,
            "workspace_id": "be5a519f-b9df-4f09-9f10-ce2f18d9a5ca",
            "is_draft": False,
            "id": app_id,
        }
    )
