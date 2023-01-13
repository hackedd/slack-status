import logging
from datetime import datetime

import requests

API_URL = "https://slack.com/api"
logger = logging.getLogger(__name__)


class Slack:
    def __init__(self, token: str, cookie: str | None = None) -> None:
        super().__init__()
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"
        if cookie:
            self.session.cookies["d"] = cookie
        self.user: str | None = None

    def auth_test(self) -> None:
        r = self.session.get(f"{API_URL}/auth.test")
        if not r.ok:  # pragma: no cover
            raise Exception(
                f"Unable to authenticate to Slack: {r.text} "
                f"({r.status_code} {r.reason})"
            )

        response = r.json()
        logger.info(f"Connected to {response['url']} as {response['user']}")
        self.user = response["user"]

    def set_status(self, text: str, emoji: str = "", expiration: int = 0) -> None:
        if not self.user:
            self.auth_test()

        request = {
            "profile": {
                "status_text": text,
                "status_emoji": emoji,
                "status_expiration": expiration,
            }
        }

        msg = f"Setting status to '{text}'"
        if emoji:
            msg += f" with emoji '{emoji}'"
        if expiration:
            msg += f" until {datetime.fromtimestamp(expiration)}"
        logger.info(msg)

        r = self.session.post(f"{API_URL}/users.profile.set", json=request)
        if not r.ok:  # pragma: no cover
            raise Exception(
                f"Unable to set Slack status: {r.text} ({r.status_code} {r.reason})"
            )

    def emoji_list(self) -> dict[str, str]:
        r = self.session.get(f"{API_URL}/emoji.list")
        r.raise_for_status()
        return r.json()["emoji"]
