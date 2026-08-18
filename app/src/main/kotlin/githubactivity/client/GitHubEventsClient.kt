package githubactivity.client

import githubactivity.error.GitHubActivityException
import githubactivity.json.JsonParseException
import githubactivity.json.JsonParser
import githubactivity.json.JsonValue
import githubactivity.model.GitHubEvent
import java.io.IOException
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.time.Duration

/**
 * Fetches a GitHub user's public event feed and maps it into typed [GitHubEvent] instances.
 *
 * Uses only the JDK's built-in java.net.http client — no external HTTP libraries.
 */
class GitHubEventsClient(
    private val httpClient: HttpClient = defaultHttpClient(),
    private val authToken: String? = System.getenv("GITHUB_TOKEN"),
) {

    companion object {
        private const val API_BASE = "https://api.github.com"
        private const val USER_AGENT = "github-activity-cli"
        private const val MAX_PER_PAGE = 100

        private fun defaultHttpClient(): HttpClient =
            HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build()
    }

    /**
     * Fetches up to [limit] recent public events for [username].
     *
     * @throws GitHubActivityException.UserNotFound if the username does not exist
     * @throws GitHubActivityException.RateLimitExceeded if the API rate limit is exhausted
     * @throws GitHubActivityException.ApiError for any other non-2xx response
     * @throws GitHubActivityException.NetworkError on connection failures
     * @throws GitHubActivityException.MalformedResponse if the body isn't valid/expected JSON
     */
    fun fetchRecentEvents(username: String, limit: Int): List<GitHubEvent> {
        val perPage = limit.coerceIn(1, MAX_PER_PAGE)
        val request = buildRequest(username, perPage)
        val response = send(request)
        handleErrorStatus(response, username)
        val events = parseEvents(response.body())
        // Defensive: per_page is a request to GitHub, not a hard contract.
        return events.take(limit)
    }

    private fun buildRequest(username: String, perPage: Int): HttpRequest {
        val builder = HttpRequest.newBuilder()
            .uri(URI.create("$API_BASE/users/$username/events?per_page=$perPage"))
            .header("Accept", "application/vnd.github+json")
            .header("X-GitHub-Api-Version", "2022-11-28")
            .header("User-Agent", USER_AGENT)
            .timeout(Duration.ofSeconds(15))
            .GET()

        if (!authToken.isNullOrBlank()) {
            builder.header("Authorization", "Bearer $authToken")
        }

        return builder.build()
    }

    private fun send(request: HttpRequest): HttpResponse<String> =
        try {
            httpClient.send(request, HttpResponse.BodyHandlers.ofString())
        } catch (e: IOException) {
            throw GitHubActivityException.NetworkError(e.message ?: "unknown I/O failure", e)
        } catch (e: InterruptedException) {
            Thread.currentThread().interrupt()
            throw GitHubActivityException.NetworkError("request interrupted", e)
        }

    private fun handleErrorStatus(response: HttpResponse<String>, username: String) {
        val status = response.statusCode()
        if (status in 200..299) return

        when {
            status == 404 -> throw GitHubActivityException.UserNotFound(username)
            status == 403 && isRateLimited(response) ->
                throw GitHubActivityException.RateLimitExceeded(rateLimitResetEpoch(response))

            else -> throw GitHubActivityException.ApiError(status, response.body().take(500))
        }
    }

    private fun isRateLimited(response: HttpResponse<String>): Boolean =
        response.headers().firstValue("x-ratelimit-remaining").orElse(null) == "0"

    private fun rateLimitResetEpoch(response: HttpResponse<String>): Long? =
        response.headers().firstValue("x-ratelimit-reset").orElse(null)?.toLongOrNull()

    private fun parseEvents(body: String): List<GitHubEvent> {
        val parsed = try {
            JsonParser.parse(body)
        } catch (e: JsonParseException) {
            throw GitHubActivityException.MalformedResponse(e.message ?: "invalid JSON")
        }

        val array = parsed as? JsonValue.JsonArray
            ?: throw GitHubActivityException.MalformedResponse("Expected top-level JSON array of events")

        return array.items.map { GitHubEvent.fromJson(it) }
    }
}
