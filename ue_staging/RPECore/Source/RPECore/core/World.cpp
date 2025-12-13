#include "core/World.h"
#include "spatial/SpatialIndex.h"
#include <algorithm>

namespace RPE {

World::World()
    : m_spatialIndex(std::make_unique<SpatialIndex>())
    , m_currentTick(0)
{
}

World::~World() = default;

Entity* World::createEntity(const std::string& id, const std::string& kind) {
    auto entity = std::make_shared<Entity>(id, kind);
    m_entities[id] = entity;
    markEntityDirty(id);
    return entity.get();
}

Entity* World::getEntity(const std::string& id) {
    auto it = m_entities.find(id);
    return it != m_entities.end() ? it->second.get() : nullptr;
}

const Entity* World::getEntity(const std::string& id) const {
    auto it = m_entities.find(id);
    return it != m_entities.end() ? it->second.get() : nullptr;
}

bool World::removeEntity(const std::string& id) {
    m_spatialIndex->removeEntity(id);
    m_dirtyEntities.erase(id);
    m_entityToRelations.erase(id);
    return m_entities.erase(id) > 0;
}

void World::addRelation(const Relation& relation) {
    m_relations.push_back(relation);
    rebuildRelationIndices();
}

void World::removeRelation(const Relation& relation) {
    // Simple removal by matching all fields
    auto it = std::remove_if(m_relations.begin(), m_relations.end(),
        [&](const Relation& r) {
            return r.getPrimitive() == relation.getPrimitive() &&
                   r.getSource() == relation.getSource() &&
                   r.getTarget() == relation.getTarget() &&
                   r.getRelationType() == relation.getRelationType();
        });

    if (it != m_relations.end()) {
        m_relations.erase(it, m_relations.end());
        rebuildRelationIndices();
    }
}

std::vector<const Relation*> World::getRelationsForEntity(const std::string& entityId) const {
    std::vector<const Relation*> result;
    auto it = m_entityToRelations.find(entityId);
    if (it != m_entityToRelations.end()) {
        for (size_t idx : it->second) {
            result.push_back(&m_relations[idx]);
        }
    }
    return result;
}

std::vector<const Relation*> World::getRelationsByPrimitive(Primitive primitive) const {
    std::vector<const Relation*> result;
    auto it = m_primitiveToRelations.find(primitive);
    if (it != m_primitiveToRelations.end()) {
        for (size_t idx : it->second) {
            result.push_back(&m_relations[idx]);
        }
    }
    return result;
}

void World::markEntityDirty(const std::string& entityId) {
    m_dirtyEntities.insert(entityId);
    if (auto* entity = getEntity(entityId)) {
        entity->markDirty();
    }
}

void World::clearDirtyFlags() {
    m_dirtyEntities.clear();
    for (auto& [id, entity] : m_entities) {
        entity->clearDirty();
    }
}

void World::rebuildRelationIndices() {
    m_entityToRelations.clear();
    m_primitiveToRelations.clear();

    for (size_t i = 0; i < m_relations.size(); ++i) {
        const auto& rel = m_relations[i];

        // Index by source entity
        m_entityToRelations[rel.getSource()].push_back(i);

        // Index by target entity if it exists
        if (rel.getTarget().has_value()) {
            m_entityToRelations[rel.getTarget().value()].push_back(i);
        }

        // Index by primitive
        m_primitiveToRelations[rel.getPrimitive()].push_back(i);
    }
}

} // namespace RPE
