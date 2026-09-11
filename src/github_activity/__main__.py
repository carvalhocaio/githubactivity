"""Composition root: wires the GitHub client into a Session and runs it."""

from __future__ import annotations

import sys

from github_activity.infrastructure.cli.session import Session
from github_activity.infrastructure.github_client import GitHubEventsClient


def main() -> None:
    client = GitHubEventsClient()
    session = Session(client=client, stdout=sys.stdout, stderr=sys.stderr)
    sys.exit(session.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
