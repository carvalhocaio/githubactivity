"""Presentation-only formatting of events to a stream."""

from __future__ import annotations

from github_activity.domain.events import GitHubEvent
from github_activity.domain.formatting import format_event


def print_events(events: list[GitHubEvent], username: str, stdout) -> None:
    if not events:
        print(f"No recent activity for {username}.", file=stdout)
        return

    for event in events:
        print(f"- {format_event(event)}", file=stdout)
