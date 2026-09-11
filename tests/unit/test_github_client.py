import json

import pytest

from github_activity.errors import (
    ApiError,
    MalformedResponseError,
    NetworkError,
    RateLimitExceededError,
    UserNotFoundError,
)
from github_activity.infrastructure.github_client import GitHubEventsClient


class TestRequestHeaders:
    def test_includes_standard_headers(self, http_opener_factory):
        captured = {}

        def opener(request):
            captured["request"] = request
            return http_opener_factory(body="[]")(request)

        client = GitHubEventsClient(opener=opener, auth_token=None)

        client.fetch_recent_events("octocat", 10)

        headers = captured["request"].headers
        assert headers["Accept"] == "application/vnd.github+json"
        assert headers["X-github-api-version"] == "2022-11-28"
        assert headers["User-agent"] == "github-activity-cli"
        assert "Authorization" not in headers

    def test_includes_authorization_when_token_given(self, http_opener_factory):
        captured = {}

        def opener(request):
            captured["request"] = request
            return http_opener_factory(body="[]")(request)

        client = GitHubEventsClient(opener=opener, auth_token="abc123")

        client.fetch_recent_events("octocat", 10)

        assert captured["request"].headers["Authorization"] == "Bearer abc123"

    def test_reads_token_from_env_by_default(self, monkeypatch, http_opener_factory):
        monkeypatch.setenv("GITHUB_TOKEN", "env-token")
        captured = {}

        def opener(request):
            captured["request"] = request
            return http_opener_factory(body="[]")(request)

        client = GitHubEventsClient(opener=opener)

        client.fetch_recent_events("octocat", 10)

        assert captured["request"].headers["Authorization"] == "Bearer env-token"

    def test_per_page_clamped_to_max(self, http_opener_factory):
        captured = {}

        def opener(request):
            captured["request"] = request
            return http_opener_factory(body="[]")(request)

        client = GitHubEventsClient(opener=opener)

        client.fetch_recent_events("octocat", 500)

        assert "per_page=100" in captured["request"].full_url

    def test_per_page_clamped_to_min(self, http_opener_factory):
        captured = {}

        def opener(request):
            captured["request"] = request
            return http_opener_factory(body="[]")(request)

        client = GitHubEventsClient(opener=opener)

        client.fetch_recent_events("octocat", 0)

        assert "per_page=1" in captured["request"].full_url


class TestFetchRecentEvents:
    def test_returns_events_sliced_to_limit(
        self, http_opener_factory, event_payload_factory
    ):
        body = json.dumps(
            [event_payload_factory("WatchEvent"), event_payload_factory("ForkEvent")]
        )
        client = GitHubEventsClient(opener=http_opener_factory(body=body))

        events = client.fetch_recent_events("octocat", 1)

        assert len(events) == 1

    def test_404_raises_user_not_found(self, http_opener_factory):
        client = GitHubEventsClient(
            opener=http_opener_factory(http_error=(404, {}, "not found"))
        )

        with pytest.raises(UserNotFoundError):
            client.fetch_recent_events("octocat", 10)

    def test_403_with_exhausted_rate_limit_raises_rate_limit_exceeded(
        self, http_opener_factory
    ):
        client = GitHubEventsClient(
            opener=http_opener_factory(
                http_error=(
                    403,
                    {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1700000000"},
                    "rate limited",
                )
            )
        )

        with pytest.raises(RateLimitExceededError) as exc_info:
            client.fetch_recent_events("octocat", 10)

        assert exc_info.value.reset_epoch_seconds == 1700000000

    def test_403_without_rate_limit_header_raises_api_error(self, http_opener_factory):
        client = GitHubEventsClient(
            opener=http_opener_factory(http_error=(403, {}, "forbidden"))
        )

        with pytest.raises(ApiError) as exc_info:
            client.fetch_recent_events("octocat", 10)

        assert exc_info.value.status_code == 403

    def test_other_non_2xx_raises_api_error_with_truncated_body(
        self, http_opener_factory
    ):
        long_body = "x" * 1000
        client = GitHubEventsClient(
            opener=http_opener_factory(http_error=(500, {}, long_body))
        )

        with pytest.raises(ApiError) as exc_info:
            client.fetch_recent_events("octocat", 10)

        assert exc_info.value.status_code == 500
        assert len(exc_info.value.body) == 500

    def test_network_failure_raises_network_error_with_cause(self, http_opener_factory):
        client = GitHubEventsClient(
            opener=http_opener_factory(url_error="connection refused")
        )

        with pytest.raises(NetworkError) as exc_info:
            client.fetch_recent_events("octocat", 10)

        assert exc_info.value.__cause__ is not None

    def test_malformed_json_body_raises_malformed_response(self, http_opener_factory):
        client = GitHubEventsClient(opener=http_opener_factory(body="not json"))

        with pytest.raises(MalformedResponseError):
            client.fetch_recent_events("octocat", 10)
