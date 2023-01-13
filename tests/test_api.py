import typing
from unittest import mock

import pytest

from slackstatus.api import API_URL, Slack


@pytest.fixture(autouse=True)
def mock_api() -> typing.Generator[mock.MagicMock, None, None]:
    with mock.patch("requests.Session") as m:
        yield m.return_value


def test_token_and_cookie(mock_api: mock.MagicMock) -> None:
    api = Slack("test-token", "test-cookie")
    assert api.session == mock_api
    mock_api.headers.__setitem__.assert_called_once_with(
        "Authorization", "Bearer test-token"
    )
    mock_api.cookies.__setitem__.assert_called_once_with("d", "test-cookie")


def test_auth(mock_api: mock.MagicMock) -> None:
    mock_api.get.return_value.json.return_value = {
        "url": "http://test.slack.com/",
        "user": "test-user",
    }

    api = Slack("test-token")
    api.auth_test()
    mock_api.get.assert_called_once_with(f"{API_URL}/auth.test")
    assert api.user == "test-user"


def test_set_status(mock_api: mock.MagicMock) -> None:
    api = Slack("test-token")
    api.user = "test-user"

    api.set_status("new status", ":tangerine:")
    mock_api.post.assert_called_once()
    (url,), kwargs = mock_api.post.call_args
    assert url == f"{API_URL}/users.profile.set"
    assert kwargs["json"]["profile"]["status_text"] == "new status"


def test_set_status_with_expiration(mock_api: mock.MagicMock) -> None:
    api = Slack("test-token")
    api.user = "test-user"

    expiration = 1234
    api.set_status("new status", expiration=expiration)
    mock_api.post.assert_called_once()
    (url,), kwargs = mock_api.post.call_args
    assert url == f"{API_URL}/users.profile.set"
    assert kwargs["json"]["profile"]["status_expiration"] == expiration


def test_set_status_retrieves_user(mock_api: mock.MagicMock) -> None:
    api = Slack("test-token")
    api.set_status("whatever")
    mock_api.get.assert_called_once_with(f"{API_URL}/auth.test")


def test_emoji_list(mock_api: mock.MagicMock) -> None:
    api = Slack("test-token")
    api.emoji_list()
    mock_api.get.assert_called_once_with(f"{API_URL}/emoji.list")
