#pragma once

#include "core/Entity.h"
#include "core/World.h"

namespace RPE {

/**
 * EntityTemplates - Factory functions for creating common entity types
 *
 * These templates provide starting configurations for entities in the
 * v0.01 prototype ecosystem simulation.
 */
class EntityTemplates {
public:
    // Create a basic agent (creature) entity
    static Entity* createAgent(World& world,
                               const std::string& id,
                               float x, float y,
                               const std::string& agentType = "herbivore");

    // Create a resource node (berry bush, etc.)
    static Entity* createResource(World& world,
                                 const std::string& id,
                                 float x, float y,
                                 float resourceAmount = 50.0f);

    // Create a predator entity
    static Entity* createPredator(World& world,
                                 const std::string& id,
                                 float x, float y);

    // Create a simple structure (player-built)
    static Entity* createStructure(World& world,
                                  const std::string& id,
                                  float x, float y,
                                  const std::string& structureType);
};

} // namespace RPE
