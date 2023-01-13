import argparse
import logging
import os
import time
from http.client import HTTPConnection

from slackstatus.api import Slack
from slackstatus.util import parse_duration


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token",
        help="Slack authentication token (environment: SLACK_TOKEN)",
        default=os.environ.get("SLACK_TOKEN"),
    )
    parser.add_argument(
        "--cookie",
        help="Slack authentication cookie (environemnt: SLACK_COOKIE)",
        default=os.environ.get("SLACK_COOKIE"),
    )
    parser.add_argument("--verbose", help="Increase logging", action="store_true")
    parser.add_argument("--debug", help="Log API requests", action="store_true")

    subparsers = parser.add_subparsers(dest="command")

    parser_set = subparsers.add_parser("set")
    parser_set.add_argument(
        "--emoji", help="Status emoji, for example :sandwich:", default=""
    )
    parser_set.add_argument("--duration", help="Automatically clear status after")
    parser_set.add_argument("text", help="Status text, for example 'Lunch'")

    subparsers.add_parser("clear")
    subparsers.add_parser("list-emoji")

    args = parser.parse_args()

    if not args.token:
        parser.error("No token specified")

    if not args.command:
        parser.error("No command specified")

    if args.debug:
        HTTPConnection.debuglevel = 1
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(level=level)

    slack = Slack(args.token, args.cookie)
    if args.command == "set":
        if args.duration:
            expiration = int(time.time()) + parse_duration(args.duration)
        else:
            expiration = 0
        slack.set_status(args.text, args.emoji, expiration)
    elif args.command == "clear":
        slack.set_status("")
    elif args.command == "list-emoji":
        emoji_list = sorted(slack.emoji_list().items())
        width = max(len(emoji) for emoji, _ in emoji_list)
        for emoji, url in emoji_list:
            print(f"{emoji:{width}}  {url}")
    else:  # pragma: no cover
        raise NotImplementedError(args.command)
