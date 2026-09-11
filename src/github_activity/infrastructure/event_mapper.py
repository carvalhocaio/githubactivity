"""Maps GitHub's Events API JSON payloads into typed GitHubEvent instances.

Kept out of the domain layer since this is a translation of one specific
external system's wire format, not a domain rule.
"""

from __future__ import annotations

import json
from typing import Any

from github_activity.domain.events import (
    Create,
    Delete,
    Fork,
    GitHubEvent,
    IssueActivity,
    IssueComment,
    PullRequest,
    Push,
    Release,
    Star,
    Unknown,
)
from github_activity.errors import MalformedResponseError


def parse_events(body: str) -> list[GitHubEvent]:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as error:
        raise MalformedResponseError(str(error)) from error

    if not isinstance(parsed, list):
        raise MalformedResponseError("expected top-level JSON array of events")

    return [event_from_payload(item) for item in parsed]


def event_from_payload(payload: Any) -> GitHubEvent:
    raw = _require_object(payload, "event")
    event_id = _require_str(raw, "id")
    event_type = _require_str(raw, "type")
    actor_login = _require_str(_require_object(raw.get("actor"), "actor"), "login")
    repo_name = _require_str(_require_object(raw.get("repo"), "repo"), "name")
    created_at = _require_str(raw, "created_at")
    event_payload = _require_object(raw.get("payload"), "payload")

    base = {
        "id": event_id,
        "actor_login": actor_login,
        "repo_name": repo_name,
        "created_at": created_at,
    }

    match event_type:
        case "PushEvent":
            ref = _optional_str(event_payload, "ref")
            branch = ref.removeprefix("refs/heads/") if ref else None
            return Push(**base, branch=branch)
        case "IssuesEvent":
            return IssueActivity(**base, action=_require_str(event_payload, "action"))
        case "IssueCommentEvent":
            return IssueComment(**base, action=_require_str(event_payload, "action"))
        case "WatchEvent":
            return Star(**base)
        case "ForkEvent":
            return Fork(**base)
        case "CreateEvent":
            return Create(
                **base,
                ref_type=_require_str(event_payload, "ref_type"),
                ref=_optional_str(event_payload, "ref"),
            )
        case "DeleteEvent":
            return Delete(
                **base,
                ref_type=_require_str(event_payload, "ref_type"),
                ref=_optional_str(event_payload, "ref"),
            )
        case "PullRequestEvent":
            return PullRequest(**base, action=_require_str(event_payload, "action"))
        case "ReleaseEvent":
            return Release(**base, action=_require_str(event_payload, "action"))
        case _:
            return Unknown(**base, raw_type=event_type)


def _require_object(value: Any, context: str) -> dict:
    if not isinstance(value, dict):
        raise MalformedResponseError(f"expected {context} to be a JSON object")
    return value


def _require_str(data: dict, key: str) -> str:
    value = data.get(key)
    if value is None:
        raise MalformedResponseError(f"missing required field '{key}'")
    if not isinstance(value, str):
        raise MalformedResponseError(f"field '{key}' expected to be a string")
    return value


def _optional_str(data: dict, key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise MalformedResponseError(f"field '{key}' expected to be a string")
    return value
