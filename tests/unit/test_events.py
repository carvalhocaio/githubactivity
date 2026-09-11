from dataclasses import FrozenInstanceError

import pytest

from github_activity.domain.events import Create, Push, Star


class TestPush:
    def test_carries_branch(self):
        event = Push(
            id="1",
            actor_login="octocat",
            repo_name="octocat/hello-world",
            created_at="2024-01-01T00:00:00Z",
            branch="main",
        )

        assert event.branch == "main"

    def test_branch_can_be_none(self):
        event = Push(
            id="1",
            actor_login="octocat",
            repo_name="octocat/hello-world",
            created_at="2024-01-01T00:00:00Z",
            branch=None,
        )

        assert event.branch is None

    def test_is_frozen(self):
        event = Push(
            id="1",
            actor_login="octocat",
            repo_name="octocat/hello-world",
            created_at="2024-01-01T00:00:00Z",
            branch="main",
        )

        with pytest.raises(FrozenInstanceError):
            event.branch = "other"


class TestCreate:
    def test_ref_can_be_none(self):
        event = Create(
            id="1",
            actor_login="octocat",
            repo_name="octocat/hello-world",
            created_at="2024-01-01T00:00:00Z",
            ref_type="repository",
            ref=None,
        )

        assert event.ref is None
        assert event.ref_type == "repository"


class TestStar:
    def test_equality_by_value(self):
        first = Star(
            id="1",
            actor_login="octocat",
            repo_name="octocat/hello-world",
            created_at="2024-01-01T00:00:00Z",
        )
        second = Star(
            id="1",
            actor_login="octocat",
            repo_name="octocat/hello-world",
            created_at="2024-01-01T00:00:00Z",
        )

        assert first == second
