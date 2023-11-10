from typing import Optional

from server.tests.mocks.util import mock_response


def get_file_response(page_id: str):
    return mock_response(
        json=[
            {
                "source": "replica",
                "id": "bea20d7f-d9a5-4467-bcd4-b0efe6a39e8d",
                "date": "2023-10-31T14:22:46.278953",
                "type": "sql",
                "page_id": page_id,
                "name": "sql1.sql",
            },
            {
                "source": "replica",
                "id": "65f1ed7f-acd0-45dd-bb86-ff0e80ef859b",
                "date": "2023-10-31T14:22:46.278953",
                "type": "data_fetcher",
                "page_id": page_id,
                "name": "function2.py",
            },
            {
                "source": "replica",
                "id": "5f1f1595-ec91-48cd-a51c-7e0a997fd463",
                "date": "2023-10-31T14:22:46.278953",
                "type": "data_fetcher",
                "page_id": page_id,
                "name": "function3.py",
            },
            {
                "source": "replica",
                "id": "d71f6373-d8dd-48c8-8c56-612c4e1ebe92",
                "date": "2023-10-31T14:22:46.278953",
                "type": "data_fetcher",
                "page_id": page_id,
                "name": "function1.py",
            },
        ]
    )


def create_file_response(req: dict):
    return mock_response(
        json={
            "source": req["source"],
            "id": "a2099d28-3da8-4094-a7a4-7d02da3ee5fd",
            "date": "2023-11-07T21:06:02.002553",
            "type": req["type"],
            "page_id": req["page_id"],
            "name": req["name"],
        }
    )


def update_file_response(
    file_id: str,
    update_data: dict,
    name: str = "mock file",
    type: str = "python",
    page_id: str = "9f1dabeb-907b-4e59-8417-ba67a801ba0e",
    source: str = "replica",
):
    return mock_response(
        json={
            "source": update_data.get("source", source),
            "id": file_id,
            "date": "2023-11-07T21:06:02.002553",
            "type": type,
            "page_id": page_id,
            "name": update_data.get("name", name),
        }
    )


def update_file_name_response(*args, **kwargs):
    # not implemented
    return mock_response(json={})


def delete_file_response(file_id: str):
    return mock_response(
        json={
            "source": "replica",
            "id": file_id,
            "date": "2023-11-07T21:06:02.002553",
            "type": "python",
            "page_id": "9f1dabeb-907b-4e59-8417-ba67a801ba0e",
            "name": "bruh2",
        }
    )
