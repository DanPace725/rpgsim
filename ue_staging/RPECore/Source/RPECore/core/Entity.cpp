#include "core/Entity.h"

namespace RPE {

Entity::Entity(const std::string& id, const std::string& kind)
    : m_id(id)
    , m_kind(kind)
    , m_dirty(false)
{
}

} // namespace RPE
