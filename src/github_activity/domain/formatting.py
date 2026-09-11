"""Converts a GitHubEvent into a single human-readable line."""

from __future__ import annotations

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


def format_event(event: GitHubEvent) -> str:
    match event:
        case Push(branch=branch, repo_name=repo_name):
            return f"Pushed to {repo_name}" + (f" ({branch})" if branch else "")
        case IssueActivity(action=action, repo_name=repo_name):
            return f"{_capitalize_first(action)} an issue in {repo_name}"
        case IssueComment(repo_name=repo_name):
            return f"Commented on an issue in {repo_name}"
        case Star(repo_name=repo_name):
            return f"Starred {repo_name}"
        case Fork(repo_name=repo_name):
            return f"Forked {repo_name}"
        case Create(ref_type=ref_type, ref=ref, repo_name=repo_name):
            return (
                f"Created {ref_type}"
                + (f" '{ref}'" if ref else "")
                + f" in {repo_name}"
            )
        case Delete(ref_type=ref_type, ref=ref, repo_name=repo_name):
            return (
                f"Deleted {ref_type}"
                + (f" '{ref}'" if ref else "")
                + f" in {repo_name}"
            )
        case PullRequest(action=action, repo_name=repo_name):
            return f"{_capitalize_first(action)} a pull request in {repo_name}"
        case Release(action=action, repo_name=repo_name):
            return f"{_capitalize_first(action)} a release in {repo_name}"
        case Unknown(raw_type=raw_type, repo_name=repo_name):
            return f"{raw_type} in {repo_name}"
        case _:
            raise AssertionError(f"unhandled event type: {type(event)!r}")


def _capitalize_first(value: str) -> str:
    return value[:1].upper() + value[1:]
