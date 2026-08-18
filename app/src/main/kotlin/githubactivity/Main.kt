package githubactivity

import githubactivity.client.GitHubEventsClient
import githubactivity.error.GitHubActivityException
import githubactivity.format.EventFormatter
import kotlin.system.exitProcess

private const val DEFAULT_LIMIT = 10

fun main(args: Array<String>) {
    val config = try {
        parseArgs(args)
    } catch (e: IllegalArgumentException) {
        System.err.println("Error: ${e.message}")
        printUsage()
        exitProcess(1)
    }

    val client = GitHubEventsClient()

    try {
        val events = client.fetchRecentEvents(config.username, config.limit)

        if (events.isEmpty()) {
            println("No recent activity for ${config.username}.")
            return
        }

        events.forEach { event ->
            println("- ${EventFormatter.format(event)}")
        }
    } catch (e: GitHubActivityException) {
        System.err.println("Error: ${e.message}")
        exitProcess(exitCodeFor(e))
    }
}

private data class Config(val username: String, val limit: Int)

private fun parseArgs(args: Array<String>): Config {
    var username: String? = null
    var limit = DEFAULT_LIMIT

    var i = 0
    while (i < args.size) {
        when (args[i]) {
            "--limit" -> {
                val value = args.getOrNull(i + 1)
                    ?: throw IllegalArgumentException("--limit requires a value")
                limit = value.toIntOrNull()?.takeIf { it > 0 }
                    ?: throw IllegalArgumentException("--limit must be a positive integer, got '$value'")
                i += 2
            }

            else -> {
                if (username != null) {
                    throw IllegalArgumentException("Unexpected argument '${args[i]}'")
                }
                username = args[i]
                i += 1
            }
        }
    }

    return Config(
        username = username ?: throw IllegalArgumentException("Username is required"),
        limit = limit,
    )
}

private fun printUsage() {
    System.err.println("Usage: github-activity <username> [--limit N]")
}

private fun exitCodeFor(e: GitHubActivityException): Int = when (e) {
    is GitHubActivityException.UserNotFound -> 2
    is GitHubActivityException.RateLimitExceeded -> 3
    is GitHubActivityException.ApiError -> 4
    is GitHubActivityException.NetworkError -> 5
    is GitHubActivityException.MalformedResponse -> 6
}
