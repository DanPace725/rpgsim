#pragma once

#include <string>
#include <unordered_map>
#include <variant>
#include <memory>

namespace RPE {

// Variant type for entity state properties
using StateValue = std::variant<int, float, double, bool, std::string>;

/**
 * Entity - A discrete world participant
 *
 * Represents any entity in the simulation world, from creatures to resources
 * to structures. Entities have identity, kind/category, and arbitrary state.
 */
class Entity {
public:
    using StateMap = std::unordered_map<std::string, StateValue>;

    Entity(const std::string& id, const std::string& kind);

    // Accessors
    const std::string& getId() const { return m_id; }
    const std::string& getKind() const { return m_kind; }

    // State management
    template<typename T>
    void setState(const std::string& key, const T& value) {
        m_state[key] = value;
    }

    template<typename T>
    T getState(const std::string& key, const T& defaultValue = T{}) const {
        auto it = m_state.find(key);
        if (it != m_state.end()) {
            if (auto* val = std::get_if<T>(&it->second)) {
                return *val;
            }
        }
        return defaultValue;
    }

    bool hasState(const std::string& key) const {
        return m_state.find(key) != m_state.end();
    }

    const StateMap& getAllState() const { return m_state; }

    // Dirty flag for change tracking
    void markDirty() { m_dirty = true; }
    void clearDirty() { m_dirty = false; }
    bool isDirty() const { return m_dirty; }

private:
    std::string m_id;
    std::string m_kind;      // category/class/template
    StateMap m_state;        // arbitrary properties (hp, hunger, position, etc.)
    bool m_dirty = false;    // tracks if entity changed this tick
};

} // namespace RPE
