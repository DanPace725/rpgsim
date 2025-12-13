#include "core/Relation.h"
#include <sstream>

namespace RPE {

Relation::Relation(Primitive primitive,
                   const std::string& source,
                   const std::string& relationType)
    : m_primitive(primitive)
    , m_source(source)
    , m_target(std::nullopt)
    , m_relationType(relationType)
    , m_payload(std::monostate{})
{
}

Relation::Relation(Primitive primitive,
                   const std::string& source,
                   const std::string& target,
                   const std::string& relationType)
    : m_primitive(primitive)
    , m_source(source)
    , m_target(target)
    , m_relationType(relationType)
    , m_payload(std::monostate{})
{
}

std::string Relation::toString() const {
    std::ostringstream oss;
    oss << primitiveToString(m_primitive) << "(" << m_source;
    if (m_target.has_value()) {
        oss << " -> " << m_target.value();
    }
    oss << ", " << m_relationType << ")";
    return oss.str();
}

const char* primitiveToString(Primitive p) {
    switch (p) {
        case Primitive::ONTOLOGY:   return "ONTOLOGY";
        case Primitive::GEOMETRY:   return "GEOMETRY";
        case Primitive::CONSTRAINT: return "CONSTRAINT";
        case Primitive::EPISTEMIC:  return "EPISTEMIC";
        case Primitive::DYNAMICS:   return "DYNAMICS";
        case Primitive::META:       return "META";
        default:                    return "UNKNOWN";
    }
}

} // namespace RPE
