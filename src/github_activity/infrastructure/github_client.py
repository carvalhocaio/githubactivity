"""Fetches a GitHub user's public event feed via the stdlib HTTP client.

Uses only ``urllib.request`` and ``json`` from the standard library, no
external HTTP dependency.
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from collections.abc import Callable

from github_activity.domain.events import GitHubEvent
from github_activity.errors import (
    ApiError,
    NetworkError,
    RateLimitExceededError,
    UserNotFoundError,
)
from github_activity.infrastructure.event_mapper import parse_events

API_BASE = "https://api.github.com"
USER_AGENT = "github-activity-cli"
MAX_PER_PAGE = 100

UrlOpener = Callable[[urllib.request.Request], "urllib.response.addinfourl"]


class GitHubEventsClient:
    def __init__(
        self,
        opener: UrlOpener = urllib.request.urlopen,
        auth_token: str | None = None,
    ) -> None:
        self._opener = opener
        self._auth_token = (
            auth_token if auth_token is not None else os.environ.get("GITHUB_TOKEN")
        )

    def fetch_recent_events(self, username: str, limit: int) -> list[GitHubEvent]:
        per_page = max(1, min(limit, MAX_PER_PAGE))
        request = self._build_request(username, per_page)
        status, headers, body = self._send(request)
        self._handle_error_status(status, headers, body, username)
        events = parse_events(body)
        return events[:limit]

    def _build_request(self, username: str, per_page: int) -> urllib.request.Request:
        url = f"{API_BASE}/users/{username}/events?per_page={per_page}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        }
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        return urllib.request.Request(url, headers=headers, method="GET")

    def _send(self, request: urllib.request.Request) -> tuple[int, dict[str, str], str]:
        try:
            with self._opener(request) as response:
                return (
                    response.status,
                    _lowercase_headers(response.headers),
                    response.read().decode(),
                )
        except urllib.error.HTTPError as error:
            return error.code, _lowercase_headers(error.headers), error.read().decode()
        except urllib.error.URLError as error:
            raise NetworkError(str(error.reason)) from error
        except OSError as error:
            raise NetworkError(str(error)) from error

    def _handle_error_status(
        self, status: int, headers: dict[str, str], body: str, username: str
    ) -> None:
        if 200 <= status < 300:
            return

        if status == 404:
            raise UserNotFoundError(username)

        if status == 403 and headers.get("x-ratelimit-remaining") == "0":
            reset = headers.get("x-ratelimit-reset")
            raise RateLimitExceededError(int(reset) if reset else None)

        raise ApiError(status, body[:500])


def _lowercase_headers(headers) -> dict[str, str]:
    return {key.lower(): value for key, value in headers.items()}
