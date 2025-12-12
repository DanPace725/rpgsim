#pragma once

#include "Entity.h"
#include "Relation.h"
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>

namespace RPE {

// Forward declarations
class SpatialIndex;

/**
 * World - The container for all entities and relations
 *
 * Manages the entity graph, relation graph, and spatial indexing.
 * Tracks dirty entities for efficient change-driven evaluation.
 */
class World {
public:
    World();
    ~World();

    // Entity management
    Entity* createEntity(const std::string& id, const std::string& kind);
    Entity* getEntity(const std::string& id);
    const Entity* getEntity(const std::string& id) const;
    bool removeEntity(const std::string& id);

    const std::unordered_map<std::string, std::shared_ptr<Entity>>& getEntities() const {
        return m_entities;
    }

    // Relation management
    void addRelation(const Relation& relation);
    void removeRelation(const Relation& relation);

    std::vector<const Relation*> getRelationsForEntity(const std::string& entityId) const;
    std::vector<const Relation*> getRelationsByPrimitive(Primitive primitive) const;

    // Dirty tracking
    void markEntityDirty(const std::string& entityId);
    const std::unordered_set<std::string>& getDirtyEntities() const { return m_dirtyEntities; }
    void clearDirtyFlags();

    // Spatial indexing
    SpatialIndex* getSpatialIndex() { return m_spatialIndex.get(); }
    const SpatialIndex* getSpatialIndex() const { return m_spatialIndex.get(); }

    // Tick counter
    uint64_t getCurrentTick() const { return m_currentTick; }
    void incrementTick() { m_currentTick++; }

private:
    std::unordered_map<std::string, std::shared_ptr<Entity>> m_entities;
    std::vector<Relation> m_relations;
    std::unordered_set<std::string> m_dirtyEntities;
    std::unique_ptr<SpatialIndex> m_spatialIndex;
    uint64_t m_currentTick = 0;

    // Index for fast relation queries
    std::unordered_map<std::string, std::vector<size_t>> m_entityToRelations;
    std::unordered_map<Primitive, std::vector<size_t>> m_primitiveToRelations;

    void rebuildRelationIndices();
};

} // namespace RPE
