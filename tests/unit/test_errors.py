import pytest

from github_activity.errors import (
    ApiError,
    GitHubActivityError,
    MalformedResponseError,
    NetworkError,
    RateLimitExceededError,
    UsageError,
    UserNotFoundError,
)


class TestUserNotFoundError:
    def test_exit_code_is_two(self):
        error = UserNotFoundError("octocat")

        assert error.exit_code == 2

    def test_message_includes_username(self):
        error = UserNotFoundError("octocat")

        assert str(error) == "User 'octocat' not found"

    def test_is_a_github_activity_error(self):
        error = UserNotFoundError("octocat")

        assert isinstance(error, GitHubActivityError)


class TestRateLimitExceededError:
    def test_exit_code_is_three(self):
        error = RateLimitExceededError(None)

        assert error.exit_code == 3

    def test_message_without_reset_epoch(self):
        error = RateLimitExceededError(None)

        assert str(error) == "GitHub API rate limit exceeded"

    def test_message_with_reset_epoch(self):
        error = RateLimitExceededError(1_700_000_000)

        assert str(error) == (
            "GitHub API rate limit exceeded. Resets at epoch 1700000000"
        )


class TestApiError:
    def test_exit_code_is_four(self):
        error = ApiError(500, "internal error")

        assert error.exit_code == 4

    def test_message_includes_status_and_body(self):
        error = ApiError(500, "internal error")

        assert str(error) == "GitHub API returned status 500: internal error"


class TestNetworkError:
    def test_exit_code_is_five(self):
        error = NetworkError("connection refused")

        assert error.exit_code == 5

    def test_message_includes_original_message(self):
        error = NetworkError("connection refused")

        assert str(error) == "Network error: connection refused"

    def test_preserves_cause_via_raise_from(self):
        cause = ConnectionError("boom")

        try:
            try:
                raise cause
            except ConnectionError as exc:
                raise NetworkError(str(exc)) from exc
        except NetworkError as error:
            assert error.__cause__ is cause


class TestMalformedResponseError:
    def test_exit_code_is_six(self):
        error = MalformedResponseError("invalid JSON")

        assert error.exit_code == 6

    def test_message_includes_original_message(self):
        error = MalformedResponseError("invalid JSON")

        assert str(error) == "Malformed API response: invalid JSON"


class TestUsageError:
    def test_is_not_a_github_activity_error(self):
        error = UsageError("Username is required")

        assert not isinstance(error, GitHubActivityError)

    def test_message_is_preserved(self):
        error = UsageError("Username is required")

        assert str(error) == "Username is required"


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
def test_exit_code_mapping(error, expected_exit_code):
    assert error.exit_code == expected_exit_code
