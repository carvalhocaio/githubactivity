"""Parses CLI arguments into a Config, without any external argparse dependency."""

from __future__ import annotations

from dataclasses import dataclass

from github_activity.errors import UsageError

DEFAULT_LIMIT = 10
USAGE = "Usage: github-activity <username> [--limit N]"


@dataclass(frozen=True, slots=True)
class Config:
    username: str
    limit: int


def parse_args(args: list[str]) -> Config:
    username: str | None = None
    limit = DEFAULT_LIMIT

    i = 0
    while i < len(args):
        if args[i] == "--limit":
            if i + 1 >= len(args):
                raise UsageError("--limit requires a value")
            value = args[i + 1]
            limit = _parse_positive_int(value)
            i += 2
        else:
            if username is not None:
                raise UsageError(f"Unexpected argument '{args[i]}'")
            username = args[i]
            i += 1

    if username is None:
        raise UsageError("Username is required")

    return Config(username=username, limit=limit)


def _parse_positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError:
        raise UsageError(f"--limit must be a positive integer, got '{value}'") from None
    if parsed <= 0:
        raise UsageError(f"--limit must be a positive integer, got '{value}'")
    return parsed


def print_usage(stderr) -> None:
    print(USAGE, file=stderr)
