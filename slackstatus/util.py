import re


def parse_duration(s: str) -> int:
    seconds = {"h": 3600, "m": 60, "s": 1}
    pat = r"(\d+)\s*(h|m|s)"
    if not re.match(f"^({pat}\\s*)+$", s, re.I):
        raise Exception(f"Unable to parse duration {s!r}")
    return sum(
        int(count) * seconds[unit.lower()] for (count, unit) in re.findall(pat, s, re.I)
    )
