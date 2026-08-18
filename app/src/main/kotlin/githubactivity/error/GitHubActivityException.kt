package githubactivity.error

/**
 * All errors this application can surface, unified under one sealed hierarchy
 * so callers can exhaustively handle every failure mode with a single `when`.
 */
sealed class GitHubActivityException(message: String, cause: Throwable? = null) :
    Exception(message, cause) {

    /** The requested GitHub username does not exist (HTTP 404). */
    data class UserNotFound(val username: String) :
        GitHubActivityException("User '$username' not found")

    /**
     * GitHub's rate limit has been exhausted (HTTP 403 combined with
     * `x-ratelimit-remaining: 0`). Distinct from a generic 403 so the CLI
     * can suggest setting GITHUB_TOKEN instead of showing a vague error.
     */
    data class RateLimitExceeded(val resetEpochSeconds: Long?) :
        GitHubActivityException(
            "GitHub API rate limit exceeded" +
                    (resetEpochSeconds?.let { ". Resets at epoch $it" } ?: "")
        )

    /** Any other non-2xx response from the API that isn't 404 or rate-limit related. */
    data class ApiError(val statusCode: Int, val body: String) :
        GitHubActivityException("GitHub API returned status $statusCode: $body")

    /** Transport-level failure: DNS, timeout, connection refused, etc. */
    data class NetworkError(val originalMessage: String, val originalCause: Throwable) :
        GitHubActivityException("Network error: $originalMessage", originalCause)

    /** The response body could not be parsed as valid JSON. */
    data class MalformedResponse(val originalMessage: String) :
        GitHubActivityException("Malformed API response: $originalMessage")
}
