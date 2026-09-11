import io

import pytest

from github_activity.domain.events import Star
from github_activity.errors import (
    ApiError,
    MalformedResponseError,
    NetworkError,
    RateLimitExceededError,
    UserNotFoundError,
)
from github_activity.infrastructure.cli.session import Session


def make_session(client):
    stdout = io.StringIO()
    stderr = io.StringIO()
    session = Session(client=client, stdout=stdout, stderr=stderr)
    return session, stdout, stderr


class TestRunSuccess:
    def test_prints_events_and_returns_zero(self, fake_client_factory):
        event = Star(
            id="1",
            actor_login="octocat",
            repo_name="octocat/hello-world",
            created_at="2024-01-01T00:00:00Z",
        )
        client = fake_client_factory(events=[event])
        session, stdout, stderr = make_session(client)

        code = session.run(["octocat"])

        assert code == 0
        assert stdout.getvalue() == "- Starred octocat/hello-world\n"
        assert stderr.getvalue() == ""

    def test_prints_no_activity_message_and_returns_zero(self, fake_client_factory):
        client = fake_client_factory(events=[])
        session, stdout, _stderr = make_session(client)

        code = session.run(["octocat"])

        assert code == 0
        assert stdout.getvalue() == "No recent activity for octocat.\n"


class TestRunUsageError:
    def test_bad_limit_returns_one_and_prints_usage(self, fake_client_factory):
        client = fake_client_factory(events=[])
        session, _stdout, stderr = make_session(client)

        code = session.run(["octocat", "--limit", "abc"])

        assert code == 1
        assert "Error:" in stderr.getvalue()
        assert "Usage:" in stderr.getvalue()


@pytest.mark.parametrize(
    ("error", "expected_exit_code"),
    [
        (UserNotFoundError("octocat"), 2),
        (RateLimitExceededError(None), 3),
        (ApiError(500, "boom"), 4),
        (NetworkError("boom"), 5),
        (MalformedResponseError("boom"), 6),
    ],
)
def test_run_maps_github_activity_errors_to_exit_codes(
    fake_client_factory, error, expected_exit_code
):
    client = fake_client_factory(error=error)
    session, _stdout, stderr = make_session(client)

    code = session.run(["octocat"])

    assert code == expected_exit_code
    assert stderr.getvalue().startswith("Error:")
