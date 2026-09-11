from __future__ import annotations

import io
import urllib.error

import pytest

from github_activity.domain.events import GitHubEvent
from github_activity.errors import GitHubActivityError


class FakeGitHubEventsClient:
    def __init__(
        self,
        events: list[GitHubEvent] | None = None,
        error: GitHubActivityError | None = None,
    ) -> None:
        self._events = events or []
        self._error = error
        self.last_call: tuple[str, int] | None = None

    def fetch_recent_events(self, username: str, limit: int) -> list[GitHubEvent]:
        self.last_call = (username, limit)
        if self._error is not None:
            raise self._error
        return self._events


def make_event_payload(event_type: str, **payload_overrides) -> dict:
    return {
        "id": "1",
        "type": event_type,
        "actor": {"login": "octocat"},
        "repo": {"name": "octocat/hello-world"},
        "created_at": "2024-01-01T00:00:00Z",
        "payload": payload_overrides,
    }


class FakeHttpResponse:
    def __init__(self, status: int, headers: dict[str, str], body: str) -> None:
        self.status = status
        self.headers = headers
        self._body = body.encode()

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> FakeHttpResponse:
        return self

    def __exit__(self, *exc_info) -> None:
        return None


def make_opener(
    status: int = 200,
    headers: dict[str, str] | None = None,
    body: str = "[]",
    http_error: tuple[int, dict[str, str], str] | None = None,
    url_error: str | None = None,
):
    def opener(request):
        if url_error is not None:
            raise urllib.error.URLError(url_error)
        if http_error is not None:
            error_status, error_headers, error_body = http_error
            raise urllib.error.HTTPError(
                request.full_url,
                error_status,
                "error",
                error_headers,
                io.BytesIO(error_body.encode()),
            )
        return FakeHttpResponse(status, headers or {}, body)

    return opener


@pytest.fixture
def http_opener_factory():
    return make_opener


@pytest.fixture
def fake_client_factory():
    return FakeGitHubEventsClient


@pytest.fixture
def event_payload_factory():
    return make_event_payload
