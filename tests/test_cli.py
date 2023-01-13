import logging
import typing
from unittest import mock

import pytest

from slackstatus.cli import main


@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLACK_TOKEN", "")
    monkeypatch.setenv("SLACK_COOKIE", "")


@pytest.fixture(autouse=True)
def mock_api() -> typing.Generator[mock.MagicMock, None, None]:
    with mock.patch("slackstatus.cli.Slack") as m:
        yield m.return_value


def test_no_token(capsys: pytest.CaptureFixture[str]) -> None:
    with mock.patch("sys.argv", new=["slack-status"]):
        with pytest.raises(SystemExit, match="2"):
            main()

    (_, err) = capsys.readouterr()
    assert "No token specified" in err


def test_no_command(capsys: pytest.CaptureFixture[str]) -> None:
    argv = "slack-status --token=1"
    with mock.patch("sys.argv", new=argv.split()):
        with pytest.raises(SystemExit, match="2"):
            main()

    (_, err) = capsys.readouterr()
    assert "No command specified" in err


@pytest.mark.parametrize(
    "arg,level",
    [
        ("--debug", logging.DEBUG),
        ("--verbose", logging.INFO),
        ("", logging.WARNING),
    ],
)
def test_log_level(arg: str, level: int) -> None:
    argv = f"slack-status --token=1 {arg} set foo"
    with mock.patch("sys.argv", new=argv.split()):
        with mock.patch("logging.basicConfig") as c:
            main()
        c.assert_called_once_with(level=level)


def test_set(mock_api: mock.MagicMock) -> None:
    argv = "slack-status --token=1 set --emoji=test status"
    with mock.patch("sys.argv", new=argv.split()):
        main()
    mock_api.set_status.assert_called_once_with("status", "test", 0)


def test_set_duration(mock_api: mock.MagicMock) -> None:
    argv = "slack-status --token=1 set --duration=30m status"
    with mock.patch("sys.argv", new=argv.split()):
        with mock.patch("time.time", return_value=0):
            main()
    mock_api.set_status.assert_called_once_with("status", "", 1800)


def test_clear(mock_api: mock.MagicMock) -> None:
    argv = "slack-status --token=1 clear"
    with mock.patch("sys.argv", new=argv.split()):
        main()
    mock_api.set_status.assert_called_once_with("")


def test_list_emoji(
    mock_api: mock.MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mock_api.emoji_list.return_value = {
        "b": "https://emoji.slack-edge.com/...",
        "a": "https://emoji.slack-edge.com/...",
        "xyz": "https://emoji.slack-edge.com/...",
    }

    argv = "slack-status --token=1 list-emoji"
    with mock.patch("sys.argv", new=argv.split()):
        main()

    (out, _) = capsys.readouterr()
    assert out.splitlines() == sorted(out.splitlines())


def test_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLACK_TOKEN", "test-token")

    argv = "slack-status clear"
    with mock.patch("sys.argv", new=argv.split()):
        with mock.patch("slackstatus.cli.Slack") as slack:
            main()

    slack.assert_called_once_with("test-token", "")


def test_cookie_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLACK_COOKIE", "test-cookie")

    argv = "slack-status --token=1 clear"
    with mock.patch("sys.argv", new=argv.split()):
        with mock.patch("slackstatus.cli.Slack") as slack:
            main()

    slack.assert_called_once_with("1", "test-cookie")
