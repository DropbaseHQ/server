from unittest.mock import Mock


def mock_response(*, json: dict, status_code: int = 200):
    return Mock(json=lambda: json, status_code=status_code)
