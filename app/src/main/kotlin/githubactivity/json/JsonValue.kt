package githubactivity.json

/**
 * Minimal representation of any JSON value.
 *
 * Not a complete JSON implementation (RFC 8259) - it's enough to model
 * GitHub's event payload without depending on an external parsing lib.
 */
sealed class JsonValue {

    data class JsonObject(val entries: Map<String, JsonValue>) : JsonValue() {
        operator fun get(key: String): JsonValue? = entries[key]
    }

    data class JsonArray(val items: List<JsonValue>) : JsonValue() {
        operator fun get(index: Int): JsonValue? = items.getOrNull(index)
    }

    data class JsonString(val value: String) : JsonValue()

    // JSON doesn't distinguish int from float at the lexical level; Double covers both cases.
    // Conversion to a specific Int/Long is left to the consumer (model/).
    data class JsonNumber(val value: Double) : JsonValue()

    data class JsonBoolean(val value: Boolean) : JsonValue()

    data object JsonNull : JsonValue()
}
