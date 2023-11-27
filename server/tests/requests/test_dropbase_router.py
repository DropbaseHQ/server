import unittest.mock
import pytest


def test_get_access_cookies_access_token_in_cookies():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.cookies.get.return_value = "mock access token"

    from server.requests.dropbase_router import get_access_cookies

    # Act
    cookies = get_access_cookies(mock_request)

    # Assert
    assert cookies.dict()["access_token_cookie"] == "mock access token"


def test_get_access_cookies_access_token_in_header():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.cookies.get.return_value = None
    mock_request.headers = {"access-token": "mock access token"}

    from server.requests.dropbase_router import get_access_cookies

    # Act
    cookies = get_access_cookies(mock_request)

    # Assert
    assert cookies.dict()["access_token_cookie"] == "mock access token"


def test_get_access_cookies_no_access_token():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.cookies.get.return_value = None
    mock_request.headers = {}

    from server.requests.dropbase_router import get_access_cookies

    # Act
    with pytest.raises(Exception):
        get_access_cookies(mock_request)


def test_get_dropbase_router_access_token_in_cookies():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.cookies.get.return_value = "mock access token"

    from server.requests.dropbase_router import get_dropbase_router

    # Act
    router = get_dropbase_router(mock_request)

    # Assert
    assert router.session.cookies.get("access_token_cookie") == "mock access token"


def test_get_dropbase_router_access_token_in_headers():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.cookies.get.return_value = None
    mock_request.headers = {"access-token": "mock access token"}

    from server.requests.dropbase_router import get_dropbase_router

    # Act
    router = get_dropbase_router(mock_request)

    # Assert
    assert router.session.cookies.get("access_token_cookie") == "mock access token"


def test_get_dropbase_router_no_access_token():
    # Arrange
    mock_request = unittest.mock.MagicMock()
    mock_request.cookies.get.return_value = None
    mock_request.headers = {}

    from server.requests.dropbase_router import get_dropbase_router

    # Act
    with pytest.raises(Exception):
        get_dropbase_router(mock_request)
