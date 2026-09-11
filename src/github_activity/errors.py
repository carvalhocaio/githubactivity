"""Centralized error hierarchy for API/network failures.

The CLI session catches ``GitHubActivityError`` once and reads ``exit_code``
off each instance to decide the process exit status, instead of a separate
dispatch function that must be kept in sync as errors are added.
"""

from __future__ import annotations


class GitHubActivityError(Exception):
    """Base for every GitHub-activity-fetching failure."""

    exit_code: int


class UserNotFoundError(GitHubActivityError):
    exit_code = 2

    def __init__(self, username: str) -> None:
        super().__init__(f"User '{username}' not found")
        self.username = username


class RateLimitExceededError(GitHubActivityError):
    exit_code = 3

    def __init__(self, reset_epoch_seconds: int | None) -> None:
        suffix = (
            f". Resets at epoch {reset_epoch_seconds}"
            if reset_epoch_seconds is not None
            else ""
        )
        super().__init__(f"GitHub API rate limit exceeded{suffix}")
        self.reset_epoch_seconds = reset_epoch_seconds


class ApiError(GitHubActivityError):
    exit_code = 4

    def __init__(self, status_code: int, body: str) -> None:
        super().__init__(f"GitHub API returned status {status_code}: {body}")
        self.status_code = status_code
        self.body = body


class NetworkError(GitHubActivityError):
    exit_code = 5

    def __init__(self, original_message: str) -> None:
        super().__init__(f"Network error: {original_message}")
        self.original_message = original_message


class MalformedResponseError(GitHubActivityError):
    exit_code = 6

    def __init__(self, original_message: str) -> None:
        super().__init__(f"Malformed API response: {original_message}")
        self.original_message = original_message


class UsageError(Exception):
    """CLI-argument error.

    Deliberately outside the GitHubActivityError hierarchy since it's raised
    before any API interaction. Always maps to exit code 1.
    """
