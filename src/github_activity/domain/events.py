"""Typed representation of a single GitHub user event.

Only the event types this app displays are modeled explicitly; anything else
falls back to ``Unknown``. Pure data, no I/O and no knowledge of the GitHub
API's JSON wire format (see ``infrastructure/event_mapper.py`` for that).

Reference: https://docs.github.com/en/rest/using-the-rest-api/github-event-types
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GitHubEvent:
    id: str
    actor_login: str
    repo_name: str
    created_at: str


@dataclass(frozen=True, slots=True)
class Push(GitHubEvent):
    branch: str | None


@dataclass(frozen=True, slots=True)
class IssueActivity(GitHubEvent):
    action: str


@dataclass(frozen=True, slots=True)
class IssueComment(GitHubEvent):
    action: str


@dataclass(frozen=True, slots=True)
class Star(GitHubEvent):
    pass


@dataclass(frozen=True, slots=True)
class Fork(GitHubEvent):
    pass


@dataclass(frozen=True, slots=True)
class Create(GitHubEvent):
    ref_type: str
    ref: str | None


@dataclass(frozen=True, slots=True)
class Delete(GitHubEvent):
    ref_type: str
    ref: str | None


@dataclass(frozen=True, slots=True)
class PullRequest(GitHubEvent):
    action: str


@dataclass(frozen=True, slots=True)
class Release(GitHubEvent):
    action: str


@dataclass(frozen=True, slots=True)
class Unknown(GitHubEvent):
    """Any event type without a dedicated rendering."""

    raw_type: str
