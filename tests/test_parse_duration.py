import pytest

from slackstatus.util import parse_duration


@pytest.mark.parametrize(
    "s,expected",
    [
        ("10s", 10),
        ("20m", 1200),
        ("2h", 7200),
        ("1h 10m 30s", 3600 + 600 + 30),
        ("1 h 10 m 30 s", 3600 + 600 + 30),
        ("1h10m30s", 3600 + 600 + 30),
    ],
)
def test_parse_duration(s: str, expected: int) -> None:
    assert (parse_duration(s)) == expected


@pytest.mark.parametrize("s", ["", "x", "1", "15x", "30s x"])
def test_parse_duration_invalid(s: str) -> None:
    with pytest.raises(Exception):
        parse_duration(s)
