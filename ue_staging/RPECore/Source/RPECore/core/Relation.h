#pragma once

#include <string>
#include <variant>
#include <optional>
#include <memory>

namespace RPE {

// The six relational primitives
enum class Primitive {
    ONTOLOGY,   // What entities are (identity, structure, composition)
    GEOMETRY,   // Where/when entities exist (spatial, temporal, causal structure)
    CONSTRAINT, // Rules that govern (bounds, limits, conservation laws)
    EPISTEMIC,  // What can be known (visibility, memory, inference)
    DYNAMICS,   // How entities change (movement, interaction, transformation)
    META        // Rules about rules (spawning, structural changes)
};

// Payload for relation data (distance, radius, resource delta, etc.)
using RelationPayload = std::variant<
    int,
    float,
    double,
    bool,
    std::string,
    std::monostate  // for relations without payload
>;

/**
 * Relation - A typed edge connecting entities or expressing a property
 *
 * Relations are the fundamental building blocks of the RPE system.
 * They describe relationships between entities according to one of
 * the six relational primitives.
 */
class Relation {
public:
    Relation(Primitive primitive,
             const std::string& source,
             const std::string& relationType);

    Relation(Primitive primitive,
             const std::string& source,
             const std::string& target,
             const std::string& relationType);

    // Accessors
    Primitive getPrimitive() const { return m_primitive; }
    const std::string& getSource() const { return m_source; }
    std::optional<std::string> getTarget() const { return m_target; }
    const std::string& getRelationType() const { return m_relationType; }

    // Payload management
    template<typename T>
    void setPayload(const T& value) {
        m_payload = value;
    }

    template<typename T>
    std::optional<T> getPayload() const {
        if (auto* val = std::get_if<T>(&m_payload)) {
            return *val;
        }
        return std::nullopt;
    }

    bool hasPayload() const {
        return !std::holds_alternative<std::monostate>(m_payload);
    }

    // Utility
    std::string toString() const;

private:
    Primitive m_primitive;
    std::string m_source;
    std::optional<std::string> m_target;  // nullopt for unary relations
    std::string m_relationType;           // e.g., "proximity", "consumes", "visibility"
    RelationPayload m_payload;
};

// Helper to convert Primitive to string
const char* primitiveToString(Primitive p);

} // namespace RPE
