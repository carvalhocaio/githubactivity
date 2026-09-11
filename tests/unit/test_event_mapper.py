import json

import pytest

from github_activity.domain.events import (
    Create,
    Delete,
    Fork,
    IssueActivity,
    IssueComment,
    PullRequest,
    Push,
    Release,
    Star,
    Unknown,
)
from github_activity.errors import MalformedResponseError
from github_activity.infrastructure.event_mapper import event_from_payload, parse_events


def make_event_payload(event_type: str, **payload_overrides) -> dict:
    return {
        "id": "1",
        "type": event_type,
        "actor": {"login": "octocat"},
        "repo": {"name": "octocat/hello-world"},
        "created_at": "2024-01-01T00:00:00Z",
        "payload": payload_overrides,
    }


class TestEventFromPayload:
    def test_push_event_strips_ref_prefix(self):
        payload = make_event_payload("PushEvent", ref="refs/heads/main")

        event = event_from_payload(payload)

        assert isinstance(event, Push)
        assert event.branch == "main"

    def test_push_event_without_ref(self):
        payload = make_event_payload("PushEvent")

        event = event_from_payload(payload)

        assert isinstance(event, Push)
        assert event.branch is None

    def test_issues_event(self):
        payload = make_event_payload("IssuesEvent", action="opened")

        event = event_from_payload(payload)

        assert isinstance(event, IssueActivity)
        assert event.action == "opened"

    def test_issue_comment_event(self):
        payload = make_event_payload("IssueCommentEvent", action="created")

        event = event_from_payload(payload)

        assert isinstance(event, IssueComment)
        assert event.action == "created"

    def test_watch_event(self):
        payload = make_event_payload("WatchEvent")

        event = event_from_payload(payload)

        assert isinstance(event, Star)

    def test_fork_event(self):
        payload = make_event_payload("ForkEvent")

        event = event_from_payload(payload)

        assert isinstance(event, Fork)

    def test_create_event(self):
        payload = make_event_payload("CreateEvent", ref_type="branch", ref="feature-x")

        event = event_from_payload(payload)

        assert isinstance(event, Create)
        assert event.ref_type == "branch"
        assert event.ref == "feature-x"

    def test_delete_event(self):
        payload = make_event_payload("DeleteEvent", ref_type="branch", ref="feature-x")

        event = event_from_payload(payload)

        assert isinstance(event, Delete)
        assert event.ref_type == "branch"

    def test_pull_request_event(self):
        payload = make_event_payload("PullRequestEvent", action="closed")

        event = event_from_payload(payload)

        assert isinstance(event, PullRequest)
        assert event.action == "closed"

    def test_release_event(self):
        payload = make_event_payload("ReleaseEvent", action="published")

        event = event_from_payload(payload)

        assert isinstance(event, Release)
        assert event.action == "published"

    def test_unknown_event_type_falls_back(self):
        payload = make_event_payload("GollumEvent")

        event = event_from_payload(payload)

        assert isinstance(event, Unknown)
        assert event.raw_type == "GollumEvent"


class TestEventFromPayloadMalformed:
    def test_missing_type(self):
        payload = make_event_payload("PushEvent")
        del payload["type"]

        with pytest.raises(MalformedResponseError):
            event_from_payload(payload)

    def test_missing_actor_login(self):
        payload = make_event_payload("PushEvent")
        payload["actor"] = {}

        with pytest.raises(MalformedResponseError):
            event_from_payload(payload)

    def test_missing_repo_name(self):
        payload = make_event_payload("PushEvent")
        payload["repo"] = {}

        with pytest.raises(MalformedResponseError):
            event_from_payload(payload)

    def test_payload_item_not_an_object(self):
        with pytest.raises(MalformedResponseError):
            event_from_payload("not-an-object")


class TestParseEvents:
    def test_invalid_json_raises_malformed_response(self):
        with pytest.raises(MalformedResponseError):
            parse_events("not json")

    def test_top_level_object_raises_malformed_response(self):
        with pytest.raises(MalformedResponseError):
            parse_events("{}")

    def test_parses_a_list_of_events(self):
        body = json.dumps([make_event_payload("WatchEvent")])

        events = parse_events(body)

        assert len(events) == 1
        assert isinstance(events[0], Star)
