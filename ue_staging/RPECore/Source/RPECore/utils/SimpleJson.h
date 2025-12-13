#pragma once

#include <string>
#include <vector>
#include <map>
#include <variant>
#include <sstream>
#include <iostream>
#include <stdexcept>

namespace Utils {

enum class JsonType {
    Null,
    Object,
    Array,
    String,
    Number,
    Boolean
};

struct JsonValue;

using JsonObject = std::map<std::string, std::shared_ptr<JsonValue>>;
using JsonArray = std::vector<std::shared_ptr<JsonValue>>;

struct JsonValue {
    JsonType type = JsonType::Null;
    std::variant<std::monostate, JsonObject, JsonArray, std::string, double, bool> value;

    // Helpers
    bool asBool() const {
        if (type == JsonType::Boolean) return std::get<bool>(value);
        return false;
    }

    double asDouble() const {
        if (type == JsonType::Number) return std::get<double>(value);
        return 0.0;
    }

    std::string asString() const {
        if (type == JsonType::String) return std::get<std::string>(value);
        return "";
    }

    const JsonObject& asObject() const {
        static JsonObject empty;
        if (type == JsonType::Object) return std::get<JsonObject>(value);
        return empty;
    }

    const JsonArray& asArray() const {
        static JsonArray empty;
        if (type == JsonType::Array) return std::get<JsonArray>(value);
        return empty;
    }
};

class SimpleJson {
public:
    static std::shared_ptr<JsonValue> parse(const std::string& json) {
        SimpleJson parser(json);
        return parser.parseValue();
    }

private:
    std::string m_json;
    size_t m_pos = 0;

    SimpleJson(const std::string& json) : m_json(json) {}

    void skipWhitespace() {
        while (m_pos < m_json.length() && (m_json[m_pos] == ' ' || m_json[m_pos] == '\t' || m_json[m_pos] == '\n' || m_json[m_pos] == '\r')) {
            m_pos++;
        }
    }

    std::shared_ptr<JsonValue> parseValue() {
        skipWhitespace();
        if (m_pos >= m_json.length()) return std::make_shared<JsonValue>();

        char c = m_json[m_pos];
        if (c == '{') return parseObject();
        if (c == '[') return parseArray();
        if (c == '"') return parseString();
        if (c == 't' || c == 'f') return parseBoolean();
        if (c == '-' || (c >= '0' && c <= '9')) return parseNumber();
        if (c == 'n') return parseNull();

        return std::make_shared<JsonValue>();
    }

    std::shared_ptr<JsonValue> parseObject() {
        auto result = std::make_shared<JsonValue>();
        result->type = JsonType::Object;
        JsonObject obj;

        m_pos++; // skip '{'
        skipWhitespace();

        if (m_json[m_pos] == '}') {
            m_pos++;
            result->value = obj;
            return result;
        }

        while (m_pos < m_json.length()) {
            skipWhitespace();
            auto keyNode = parseString();
            std::string key = keyNode->asString();

            skipWhitespace();
            if (m_json[m_pos] != ':') throw std::runtime_error("Expected ':'");
            m_pos++; // skip ':'

            obj[key] = parseValue();

            skipWhitespace();
            if (m_json[m_pos] == '}') {
                m_pos++;
                break;
            }
            if (m_json[m_pos] != ',') throw std::runtime_error("Expected ',' or '}'");
            m_pos++; // skip ','
        }

        result->value = obj;
        return result;
    }

    std::shared_ptr<JsonValue> parseArray() {
        auto result = std::make_shared<JsonValue>();
        result->type = JsonType::Array;
        JsonArray arr;

        m_pos++; // skip '['
        skipWhitespace();

        if (m_json[m_pos] == ']') {
            m_pos++;
            result->value = arr;
            return result;
        }

        while (m_pos < m_json.length()) {
            arr.push_back(parseValue());

            skipWhitespace();
            if (m_json[m_pos] == ']') {
                m_pos++;
                break;
            }
            if (m_json[m_pos] != ',') throw std::runtime_error("Expected ',' or ']'");
            m_pos++; // skip ','
        }

        result->value = arr;
        return result;
    }

    std::shared_ptr<JsonValue> parseString() {
        auto result = std::make_shared<JsonValue>();
        result->type = JsonType::String;
        std::string str;

        m_pos++; // skip '"'

        while (m_pos < m_json.length()) {
            char c = m_json[m_pos];
            if (c == '"') {
                m_pos++;
                break;
            }
            if (c == '\\') {
                m_pos++;
                // Handle basic escapes if needed, for now just skip
            }
            str += m_json[m_pos];
            m_pos++;
        }

        result->value = str;
        return result;
    }

    std::shared_ptr<JsonValue> parseNumber() {
        auto result = std::make_shared<JsonValue>();
        result->type = JsonType::Number;
        size_t start = m_pos;

        while (m_pos < m_json.length() && (isdigit(m_json[m_pos]) || m_json[m_pos] == '.' || m_json[m_pos] == '-' || m_json[m_pos] == 'e' || m_json[m_pos] == 'E')) {
            m_pos++;
        }

        std::string numStr = m_json.substr(start, m_pos - start);
        result->value = std::stod(numStr);
        return result;
    }

    std::shared_ptr<JsonValue> parseBoolean() {
        auto result = std::make_shared<JsonValue>();
        result->type = JsonType::Boolean;

        if (m_json.substr(m_pos, 4) == "true") {
            result->value = true;
            m_pos += 4;
        } else if (m_json.substr(m_pos, 5) == "false") {
            result->value = false;
            m_pos += 5;
        }

        return result;
    }

    std::shared_ptr<JsonValue> parseNull() {
        auto result = std::make_shared<JsonValue>();
        result->type = JsonType::Null;
        m_pos += 4; // null
        return result;
    }
};

} // namespace Utils
