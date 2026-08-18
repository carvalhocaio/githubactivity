package githubactivity.model

import githubactivity.error.GitHubActivityException
import githubactivity.json.JsonValue

/**
 * Typed representation of a single GitHub user event, built from the raw
 * JSON returned by the Events API. Only the event types this app displays
 * are modeled explicitly; anything else falls back to [Unknown].
 *
 * Reference: https://docs.github.com/en/rest/using-the-rest-api/github-event-types
 */
sealed class GitHubEvent {
    abstract val id: String
    abstract val actorLogin: String
    abstract val repoName: String
    abstract val createdAt: String

    data class Push(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
        val commitCount: Int,
    ) : GitHubEvent()

    data class IssueActivity(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
        val action: String,
    ) : GitHubEvent()

    data class IssueComment(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
        val action: String,
    ) : GitHubEvent()

    data class Star(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
    ) : GitHubEvent()

    data class Fork(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
    ) : GitHubEvent()

    data class Create(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
        val refType: String,
        val ref: String?,
    ) : GitHubEvent()

    data class Delete(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
        val refType: String,
        val ref: String?,
    ) : GitHubEvent()

    data class PullRequest(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
        val action: String,
    ) : GitHubEvent()

    data class Release(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
        val action: String,
    ) : GitHubEvent()

    /** Any event type without a dedicated rendering — falls back to a generic message. */
    data class Unknown(
        override val id: String,
        override val actorLogin: String,
        override val repoName: String,
        override val createdAt: String,
        val rawType: String,
    ) : GitHubEvent()

    companion object {
        fun fromJson(json: JsonValue): GitHubEvent {
            val obj = json.asObject("event")
            val id = obj.requireString("id")
            val type = obj.requireString("type")
            val actorLogin = obj.requireObject("actor").requireString("login")
            val repoName = obj.requireObject("repo").requireString("name")
            val createdAt = obj.requireString("created_at")
            val payload = obj.requireObject("payload")

            return when (type) {
                "PushEvent" -> Push(
                    id, actorLogin, repoName, createdAt,
                    commitCount = (payload["commits"] as? JsonValue.JsonArray)?.items?.size ?: 0,
                )

                "IssuesEvent" -> IssueActivity(
                    id, actorLogin, repoName, createdAt,
                    action = payload.requireString("action"),
                )

                "IssueCommentEvent" -> IssueComment(
                    id, actorLogin, repoName, createdAt,
                    action = payload.requireString("action"),
                )

                "WatchEvent" -> Star(id, actorLogin, repoName, createdAt)

                "ForkEvent" -> Fork(id, actorLogin, repoName, createdAt)

                "CreateEvent" -> Create(
                    id, actorLogin, repoName, createdAt,
                    refType = payload.requireString("ref_type"),
                    ref = payload.optionalString("ref"),
                )

                "DeleteEvent" -> Delete(
                    id, actorLogin, repoName, createdAt,
                    refType = payload.requireString("ref_type"),
                    ref = payload.optionalString("ref"),
                )

                "PullRequestEvent" -> PullRequest(
                    id, actorLogin, repoName, createdAt,
                    action = payload.requireString("action"),
                )

                "ReleaseEvent" -> Release(
                    id, actorLogin, repoName, createdAt,
                    action = payload.requireString("action"),
                )

                else -> Unknown(id, actorLogin, repoName, createdAt, rawType = type)
            }
        }
    }
}

// --- Safe-cast helpers scoped to this file ---------------------------------
// Kept here rather than in JsonValue.kt because the error messages and the
// choice of which fields are "required" are domain decisions, not generic
// JSON concerns.

private fun JsonValue.asObject(context: String): JsonValue.JsonObject =
    this as? JsonValue.JsonObject
        ?: throw GitHubActivityException.MalformedResponse("Expected $context to be a JSON object")

private fun JsonValue.JsonObject.requireString(key: String): String {
    val value = entries[key]
        ?: throw GitHubActivityException.MalformedResponse("Missing required field '$key'")
    return (value as? JsonValue.JsonString)?.value
        ?: throw GitHubActivityException.MalformedResponse("Field '$key' expected to be a string")
}

private fun JsonValue.JsonObject.requireObject(key: String): JsonValue.JsonObject {
    val value = entries[key]
        ?: throw GitHubActivityException.MalformedResponse("Missing required field '$key'")
    return value as? JsonValue.JsonObject
        ?: throw GitHubActivityException.MalformedResponse("Field '$key' expected to be an object")
}

private fun JsonValue.JsonObject.optionalString(key: String): String? {
    val value = entries[key] ?: return null
    return (value as? JsonValue.JsonString)?.value
}
