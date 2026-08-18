package githubactivity.json

/**
 * Erro de parsing com posição no input, pra mensagens de erro úteis
 * em vez de "algo deu errado no JSON".
 */
class JsonParseException(message: String, val position: Int) :
    Exception("$message (position $position)")

/**
 * Parser JSON recursivo-descendente, escrito à mão pra manter o projeto
 * livre de dependências externas (RFC 8259, com escopo reduzido ao que
 * a API do GitHub de fato retorna — sem validação estrita de edge cases
 * como zeros à esquerda em números).
 */
class JsonParser private constructor(private val input: String) {

    private var pos = 0

    companion object {
        fun parse(input: String): JsonValue {
            val parser = JsonParser(input)
            val value = parser.parseValue()
            parser.skipWhitespace()
            if (!parser.isAtEnd()) {
                throw JsonParseException("Unexpected trailing content", parser.pos)
            }
            return value
        }
    }

    private fun parseValue(): JsonValue {
        skipWhitespace()
        if (isAtEnd()) throw JsonParseException("Unexpected end of input", pos)
        return when (peek()) {
            '{' -> parseObject()
            '[' -> parseArray()
            '"' -> parseString()
            't', 'f' -> parseBoolean()
            'n' -> parseNull()
            '-', in '0'..'9' -> parseNumber()
            else -> throw JsonParseException("Unexpected character '${peek()}'", pos)
        }
    }

    private fun parseObject(): JsonValue.JsonObject {
        expect('{')
        val entries = mutableMapOf<String, JsonValue>()
        skipWhitespace()
        if (peekOrNull() == '}') {
            advance()
            return JsonValue.JsonObject(entries)
        }
        while (true) {
            skipWhitespace()
            val key = parseString().value
            skipWhitespace()
            expect(':')
            entries[key] = parseValue()
            skipWhitespace()
            when (peekOrNull()) {
                ',' -> advance()
                '}' -> {
                    advance(); return JsonValue.JsonObject(entries)
                }

                else -> throw JsonParseException("Expected ',' or '}' in object", pos)
            }
        }
    }

    private fun parseArray(): JsonValue.JsonArray {
        expect('[')
        val items = mutableListOf<JsonValue>()
        skipWhitespace()
        if (peekOrNull() == ']') {
            advance()
            return JsonValue.JsonArray(items)
        }
        while (true) {
            items.add(parseValue())
            skipWhitespace()
            when (peekOrNull()) {
                ',' -> advance()
                ']' -> {
                    advance(); return JsonValue.JsonArray(items)
                }

                else -> throw JsonParseException("Expected ',' or ']' in array", pos)
            }
        }
    }

    private fun parseString(): JsonValue.JsonString {
        expect('"')
        val sb = StringBuilder()
        while (true) {
            if (isAtEnd()) throw JsonParseException("Unterminated string", pos)
            when (val c = advance()) {
                '"' -> return JsonValue.JsonString(sb.toString())
                '\\' -> sb.append(parseEscape())
                else -> sb.append(c)
            }
        }
    }

    private fun parseEscape(): Char {
        if (isAtEnd()) throw JsonParseException("Unterminated escape sequence", pos)
        return when (val c = advance()) {
            '"' -> '"'
            '\\' -> '\\'
            '/' -> '/'
            'b' -> '\b'
            'f' -> '\u000C'
            'n' -> '\n'
            'r' -> '\r'
            't' -> '\t'
            'u' -> parseUnicodeEscape()
            else -> throw JsonParseException("Invalid escape character '\\$c'", pos)
        }
    }

    private fun parseUnicodeEscape(): Char {
        if (pos + 4 > input.length) throw JsonParseException("Incomplete unicode escape", pos)
        val hex = input.substring(pos, pos + 4)
        val code = hex.toIntOrNull(16)
            ?: throw JsonParseException("Invalid unicode escape '\\u$hex'", pos)
        pos += 4
        return code.toChar()
    }

    private fun parseNumber(): JsonValue.JsonNumber {
        val start = pos
        if (peekOrNull() == '-') advance()
        while (peekOrNull()?.isDigit() == true) advance()
        if (peekOrNull() == '.') {
            advance()
            while (peekOrNull()?.isDigit() == true) advance()
        }
        if (peekOrNull() == 'e' || peekOrNull() == 'E') {
            advance()
            if (peekOrNull() == '+' || peekOrNull() == '-') advance()
            while (peekOrNull()?.isDigit() == true) advance()
        }
        val text = input.substring(start, pos)
        val value = text.toDoubleOrNull()
            ?: throw JsonParseException("Invalid number '$text'", start)
        return JsonValue.JsonNumber(value)
    }

    private fun parseBoolean(): JsonValue.JsonBoolean = when {
        matchLiteral("true") -> JsonValue.JsonBoolean(true)
        matchLiteral("false") -> JsonValue.JsonBoolean(false)
        else -> throw JsonParseException("Invalid literal", pos)
    }

    private fun parseNull(): JsonValue =
        if (matchLiteral("null")) JsonValue.JsonNull
        else throw JsonParseException("Invalid literal", pos)

    private fun matchLiteral(literal: String): Boolean {
        if (!input.startsWith(literal, pos)) return false
        pos += literal.length
        return true
    }

    private fun isAtEnd(): Boolean = pos >= input.length
    private fun peek(): Char = input[pos]
    private fun peekOrNull(): Char? = if (isAtEnd()) null else input[pos]
    private fun advance(): Char = input[pos++]

    private fun expect(c: Char) {
        if (isAtEnd() || input[pos] != c) {
            throw JsonParseException("Expected '$c'", pos)
        }
        pos++
    }

    private fun skipWhitespace() {
        while (!isAtEnd() && peek().isWhitespace()) advance()
    }
}
