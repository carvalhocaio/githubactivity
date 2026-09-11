import pytest

from github_activity.domain import events
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
from github_activity.domain.formatting import format_event

_BASE = {
    "id": "1",
    "actor_login": "octocat",
    "repo_name": "octocat/hello-world",
    "created_at": "2024-01-01T00:00:00Z",
}


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        (Push(**_BASE, branch="main"), "Pushed to octocat/hello-world (main)"),
        (Push(**_BASE, branch=None), "Pushed to octocat/hello-world"),
        (
            IssueActivity(**_BASE, action="opened"),
            "Opened an issue in octocat/hello-world",
        ),
        (
            IssueComment(**_BASE, action="created"),
            "Commented on an issue in octocat/hello-world",
        ),
        (Star(**_BASE), "Starred octocat/hello-world"),
        (Fork(**_BASE), "Forked octocat/hello-world"),
        (
            Create(**_BASE, ref_type="branch", ref="feature-x"),
            "Created branch 'feature-x' in octocat/hello-world",
        ),
        (
            Create(**_BASE, ref_type="repository", ref=None),
            "Created repository in octocat/hello-world",
        ),
        (
            Delete(**_BASE, ref_type="branch", ref="feature-x"),
            "Deleted branch 'feature-x' in octocat/hello-world",
        ),
        (
            PullRequest(**_BASE, action="closed"),
            "Closed a pull request in octocat/hello-world",
        ),
        (
            Release(**_BASE, action="published"),
            "Published a release in octocat/hello-world",
        ),
        (
            Unknown(**_BASE, raw_type="GollumEvent"),
            "GollumEvent in octocat/hello-world",
        ),
    ],
)
def test_format_event(event, expected):
    assert format_event(event) == expected


def test_every_event_subclass_is_handled():
    for subclass in events.GitHubEvent.__subclasses__():
        instance = _build_minimal(subclass)

        format_event(instance)


def _build_minimal(subclass: type[GitHubEvent]) -> GitHubEvent:
    extra_defaults = {
        "branch": None,
        "action": "opened",
        "ref_type": "branch",
        "ref": None,
        "raw_type": "SomeEvent",
    }
    field_names = subclass.__dataclass_fields__.keys()
    extra_fields = {
        name: extra_defaults[name] for name in field_names if name not in _BASE
    }
    return subclass(**_BASE, **extra_fields)
