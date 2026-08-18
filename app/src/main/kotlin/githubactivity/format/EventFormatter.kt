package githubactivity.format

import githubactivity.model.GitHubEvent

/**
 * Converts a [GitHubEvent] into a single human-readable line, matching the
 * style requested by the roadmap.sh spec (e.g. "Pushed 3 commits to owner/repo").
 */
object EventFormatter {

    fun format(event: GitHubEvent): String = when (event) {
        is GitHubEvent.Push ->
            "Pushed to ${event.repoName}" + (event.branch?.let { " ($it)" } ?: "")

        is GitHubEvent.IssueActivity ->
            "${event.action.replaceFirstChar { it.uppercase() }} an issue in ${event.repoName}"

        is GitHubEvent.IssueComment ->
            "Commented on an issue in ${event.repoName}"

        is GitHubEvent.Star ->
            "Starred ${event.repoName}"

        is GitHubEvent.Fork ->
            "Forked ${event.repoName}"

        is GitHubEvent.Create ->
            "Created ${event.refType}${event.ref?.let { " '$it'" } ?: ""} in ${event.repoName}"

        is GitHubEvent.Delete ->
            "Deleted ${event.refType}${event.ref?.let { " '$it'" } ?: ""} in ${event.repoName}"

        is GitHubEvent.PullRequest ->
            "${event.action.replaceFirstChar { it.uppercase() }} a pull request in ${event.repoName}"

        is GitHubEvent.Release ->
            "${event.action.replaceFirstChar { it.uppercase() }} a release in ${event.repoName}"

        is GitHubEvent.Unknown ->
            "${event.rawType} in ${event.repoName}"
    }

    private fun commitWord(count: Int): String = if (count == 1) "commit" else "commits"
}
