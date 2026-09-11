import io

from github_activity.domain.events import Star
from github_activity.infrastructure.cli.output import print_events
from github_activity.infrastructure.cli.parser import USAGE, print_usage


class TestPrintEvents:
    def test_prints_no_activity_message_when_empty(self):
        stdout = io.StringIO()

        print_events([], "octocat", stdout)

        assert stdout.getvalue() == "No recent activity for octocat.\n"

    def test_prints_a_dash_prefixed_line_per_event(self):
        stdout = io.StringIO()
        event = Star(
            id="1",
            actor_login="octocat",
            repo_name="octocat/hello-world",
            created_at="2024-01-01T00:00:00Z",
        )

        print_events([event], "octocat", stdout)

        assert stdout.getvalue() == "- Starred octocat/hello-world\n"


class TestPrintUsage:
    def test_prints_usage_string(self):
        stderr = io.StringIO()

        print_usage(stderr)

        assert stderr.getvalue() == USAGE + "\n"
