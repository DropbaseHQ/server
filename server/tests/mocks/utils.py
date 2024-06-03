from unittest.mock import Mock


def mock_response(*, json: dict, status_code: int = 200, **kwargs):
    return Mock(json=lambda: json, status_code=status_code, **kwargs)
