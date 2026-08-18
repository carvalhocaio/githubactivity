# github-activity

A command-line tool that fetches a GitHub user's recent public activity and
displays it in the terminal — built from scratch with zero external
dependencies, including a hand-written JSON parser.

## Features

- Fetches recent public events for any GitHub user via the GitHub REST API
- Zero external dependencies: uses only `java.net.http` (JDK stdlib) for
  networking and a custom recursive-descent parser for JSON
- Graceful error handling with distinct exit codes for scripting
  (invalid username, rate limiting, network failures, malformed responses)
- Optional `GITHUB_TOKEN` support to raise the rate limit from 60 to 5,000
  requests/hour
- Configurable result limit via `--limit`

## Requirements

- JDK 21+
- No API token required for basic usage (subject to GitHub's unauthenticated
  rate limit of 60 requests/hour)

## Usage

```bash
./gradlew run --args="<username>"
./gradlew run --args="<username> --limit 5"
```

Example:

```bash
./gradlew run --args="carvalhocaio"
```

```
- Pushed to carvalhocaio/developer-roadmap (main)
- Starred carvalhocaio/developer-roadmap
- Opened a pull request in carvalhocaio/developer-roadmap
```

### Building a standalone JAR

```bash
./gradlew build
java -jar app/build/libs/app-0.1.0.jar <username>
```

### Authenticated requests (optional)

Set `GITHUB_TOKEN` in your environment to raise the rate limit:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
./gradlew run --args="<username>"
```

## Exit codes

| Code | Meaning                                 |
| ---- | --------------------------------------- |
| 0    | Success                                 |
| 1    | Invalid usage (bad/missing arguments)   |
| 2    | GitHub user not found                   |
| 3    | GitHub API rate limit exceeded          |
| 4    | Other non-2xx GitHub API response       |
| 5    | Network error                           |
| 6    | Malformed API response                  |

## Project structure

```
app/src/main/kotlin/githubactivity/
├── Main.kt                      # entry point, arg parsing, orchestration
├── client/
│   └── GitHubEventsClient.kt    # HTTP fetching, status/error mapping
├── json/
│   ├── JsonValue.kt             # minimal JSON value representation
│   └── JsonParser.kt            # hand-written recursive-descent parser
├── model/
│   └── GitHubEvent.kt           # typed events, built from JsonValue
├── format/
│   └── EventFormatter.kt        # GitHubEvent -> human-readable line
└── error/
    └── GitHubActivityException.kt  # sealed hierarchy of failure modes
```

## Design notes

- **No `commits` count on push events.** The GitHub Events API
  (`/users/{username}/events`) does not include a `commits` array or count
  in `PushEvent` payloads — that field only exists in webhook payloads, a
  different format. Rather than burn an extra API call per push event to
  fetch the real count via the compare endpoint, this tool surfaces the
  branch name instead, which the API does provide for free.
- **Sealed class hierarchies** (`GitHubEvent`, `GitHubActivityException`)
  are used throughout so that `when` expressions over them are exhaustive
  and compiler-checked — adding a new event type or error case forces every
  relevant `when` to be updated.

## Project origin

Built as an implementation of the
[GitHub User Activity](https://roadmap.sh/projects/github-user-activity)
project from [roadmap.sh](https://roadmap.sh).
