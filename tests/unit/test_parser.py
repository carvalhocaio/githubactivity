import pytest

from github_activity.errors import UsageError
from github_activity.infrastructure.cli.parser import Config, parse_args


class TestParseArgsValid:
    def test_username_only_uses_default_limit(self):
        config = parse_args(["octocat"])

        assert config == Config(username="octocat", limit=10)

    def test_username_with_limit_flag(self):
        config = parse_args(["octocat", "--limit", "5"])

        assert config == Config(username="octocat", limit=5)

    def test_limit_flag_before_username(self):
        config = parse_args(["--limit", "5", "octocat"])

        assert config == Config(username="octocat", limit=5)


class TestParseArgsInvalid:
    def test_missing_username_raises_usage_error(self):
        with pytest.raises(UsageError, match="Username is required"):
            parse_args([])

    def test_limit_without_value_raises_usage_error(self):
        with pytest.raises(UsageError, match="--limit requires a value"):
            parse_args(["octocat", "--limit"])

    def test_limit_non_integer_raises_usage_error(self):
        with pytest.raises(UsageError, match="positive integer"):
            parse_args(["octocat", "--limit", "abc"])

    def test_limit_zero_raises_usage_error(self):
        with pytest.raises(UsageError, match="positive integer"):
            parse_args(["octocat", "--limit", "0"])

    def test_limit_negative_raises_usage_error(self):
        with pytest.raises(UsageError, match="positive integer"):
            parse_args(["octocat", "--limit", "-5"])

    def test_unexpected_extra_argument_raises_usage_error(self):
        with pytest.raises(UsageError, match="Unexpected argument"):
            parse_args(["octocat", "someone-else"])
