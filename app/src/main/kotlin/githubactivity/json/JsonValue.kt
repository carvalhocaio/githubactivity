package githubactivity.json

/**
 * Representação mínima de qualque valor JSON.
 *
 * Não é um JSON completo (RFC 8529) - é o suficiente para modelar o payload
 * de eventos do GitHub sem depender de uma lib externa de parsing.
 */
sealed class JsonValue {

    data class JsonObject(val entries: Map<String, JsonValue>) : JsonValue() {
        operator fun get(key: String): JsonValue? = entries[key]
    }

    data class JsonArray(val items: List<JsonValue>) : JsonValue() {
        operator fun get(index: Int): JsonValue? = items.getOrNull(index)
    }

    data class JsonString(val value: String) : JsonValue()

    // JSON não distingue int de float no nível léxico; Double cobre os dois casos.
    // Conversão pra Int/Long específico fica a cargo de quem consome (model/).
    data class JsonNumber(val value: Double) : JsonValue()

    data class JsonBoolean(val value: Boolean) : JsonValue()

    data object JsonNull : JsonValue()
}
