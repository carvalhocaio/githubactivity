"""Orchestrates a single CLI invocation: parse args, fetch, print, exit code."""

from __future__ import annotations

from github_activity.errors import GitHubActivityError, UsageError
from github_activity.infrastructure.cli.output import print_events
from github_activity.infrastructure.cli.parser import parse_args, print_usage


class Session:
    def __init__(self, client, stdout, stderr) -> None:
        self._client = client
        self._stdout = stdout
        self._stderr = stderr

    def run(self, argv: list[str]) -> int:
        try:
            config = parse_args(argv)
        except UsageError as error:
            print(f"Error: {error}", file=self._stderr)
            print_usage(self._stderr)
            return 1

        try:
            events = self._client.fetch_recent_events(config.username, config.limit)
        except GitHubActivityError as error:
            print(f"Error: {error}", file=self._stderr)
            return error.exit_code

        print_events(events, config.username, self._stdout)
        return 0
