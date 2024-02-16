import unittest.mock
import pytest


def test_get_access_cookies_access_token_in_header():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.headers = {"access-token": "mock access token"}

    from server.requests.dropbase_router import get_server_access_header

    # Act
    access_token = get_server_access_header(mock_request)

    # Assert
    assert access_token == "mock access token"


def test_get_access_cookies_no_access_token():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.headers = {}

    from server.requests.dropbase_router import get_server_access_header

    # Act
    with pytest.raises(Exception):
        get_server_access_header(mock_request)


def test_get_dropbase_router_access_token_in_headers():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.headers = {"access-token": "mock access token"}

    from server.requests.dropbase_router import get_dropbase_router

    # Act
    router = get_dropbase_router(mock_request)

    # Assert
    assert router.session.headers.get("Authorization") == "Bearer mock access token"


def test_get_dropbase_router_no_access_token():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.cookies.get.return_value = None
    mock_request.headers = {}

    from server.requests.dropbase_router import get_dropbase_router

    # Act
    with pytest.raises(Exception):
        get_dropbase_router(mock_request)
