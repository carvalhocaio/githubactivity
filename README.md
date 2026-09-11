# github-activity

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![uv](https://img.shields.io/badge/package%20manager-uv-blueviolet)
![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC)
![Ruff](https://img.shields.io/badge/lint%2Fformat-ruff-red)

A command-line tool that fetches a GitHub user's recent public activity and
displays it in the terminal — built with zero external dependencies, using
only the Python standard library for networking and JSON parsing.

![Demo](assets/demo.gif)

## Features

- Fetches recent public events for any GitHub user via the GitHub REST API
- Zero external dependencies: uses only `urllib.request` and `json` from the
  standard library
- Graceful error handling with distinct exit codes for scripting
  (invalid username, rate limiting, network failures, malformed responses)
- Optional `GITHUB_TOKEN` support to raise the rate limit from 60 to 5,000
  requests/hour
- Configurable result limit via `--limit`

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- No API token required for basic usage (subject to GitHub's unauthenticated
  rate limit of 60 requests/hour)

## Usage

```bash
git clone https://github.com/carvalhocaio/githubactivity.git
cd githubactivity
uv run github-activity <username>
uv run github-activity <username> --limit 5
```

Example:

```bash
uv run github-activity carvalhocaio
```

```
- Pushed to carvalhocaio/developer-roadmap (main)
- Starred carvalhocaio/developer-roadmap
- Opened a pull request in carvalhocaio/developer-roadmap
```

### Authenticated requests (optional)

Set `GITHUB_TOKEN` in your environment to raise the rate limit:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
uv run github-activity <username>
```

## Development

```bash
make sync    # install runtime + dev dependencies
make test    # run tests (pytest -v)
make lint    # run linter (ruff check)
make format  # format code (ruff format)
make check   # lint + format-check + test
```

To regenerate the demo GIF, see the version note at the top of
`assets/demo.tape` before running `vhs assets/demo.tape`.

## Exit codes

| Code | Meaning                               |
| ---- | ------------------------------------- |
| 0    | Success                               |
| 1    | Invalid usage (bad/missing arguments) |
| 2    | GitHub user not found                 |
| 3    | GitHub API rate limit exceeded        |
| 4    | Other non-2xx GitHub API response     |
| 5    | Network error                         |
| 6    | Malformed API response                |

## Project structure

```
src/github_activity/
├── __main__.py             # composition root
├── errors.py               # GitHubActivityError hierarchy + UsageError
├── domain/
│   ├── events.py           # GitHubEvent + typed variants (pure, no I/O)
│   └── formatting.py       # GitHubEvent -> human-readable line
└── infrastructure/
    ├── event_mapper.py     # GitHub JSON payload -> typed GitHubEvent
    ├── github_client.py    # HTTP fetching, status/error mapping
    └── cli/
        ├── parser.py       # argument parsing
        ├── output.py       # printing events to a stream
        └── session.py      # orchestration + exit-code dispatch
```

## Design notes

- **No `commits` count on push events.** The GitHub Events API
  (`/users/{username}/events`) does not include a `commits` array or count
  in `PushEvent` payloads — that field only exists in webhook payloads, a
  different format. Rather than burn an extra API call per push event to
  fetch the real count via the compare endpoint, this tool surfaces the
  branch name instead, which the API does provide for free.
- **No `application` layer or repository `Protocol`.** Unlike a project with
  swappable persistence, this tool has exactly one real integration (the
  GitHub API) and nothing to swap it for, so a ports-and-adapters
  abstraction would be speculative generality. `domain/` stays pure and
  `infrastructure/` holds the HTTP client and CLI; `Session` depends on the
  client through constructor injection, which is enough to substitute a
  fake in tests without a `Protocol`.
- **Exhaustiveness via tests, not the compiler.** `GitHubEvent` variants are
  frozen, slotted dataclasses matched with `match`/`case` in
  `domain/formatting.py`. Python has no sealed-class enforcement, so a
  dedicated test iterates `GitHubEvent.__subclasses__()` to guarantee every
  variant has a formatting branch — a test-driven substitute for the
  compiler-checked exhaustiveness a sealed hierarchy would give in a
  language like Kotlin.
- **No `rich` dependency.** Output is plain, uncolored text, matching the
  original implementation; adding a dependency purely for color would be
  scope the tool never asked for.

## Project origin

Built as an implementation of the
[GitHub User Activity](https://roadmap.sh/projects/github-user-activity)
project from [roadmap.sh](https://roadmap.sh). Originally implemented in
Kotlin, later rewritten in Python.
