#include "primitives/EntityTemplates.h"

namespace RPE {

Entity* EntityTemplates::createAgent(World& world,
                                    const std::string& id,
                                    float x, float y,
                                    const std::string& agentType) {
    Entity* agent = world.createEntity(id, "agent");

    // ONTOLOGY - What it is
    agent->setState("agent_type", agentType);

    // GEOMETRY - Where it is
    agent->setState("x", x);
    agent->setState("y", y);

    // DYNAMICS - Movement and behavior
    agent->setState("speed", 1.0f);
    agent->setState("vel_x", 0.0f);
    agent->setState("vel_y", 0.0f);

    // CONSTRAINT - Bounds and limits
    agent->setState("health", 100.0f);
    agent->setState("max_health", 100.0f);
    agent->setState("energy", 100.0f);
    agent->setState("max_energy", 100.0f);
    agent->setState("hunger", 0.0f);

    // EPISTEMIC - What it can sense
    agent->setState("vision_range", 80.0f);

    return agent;
}

Entity* EntityTemplates::createResource(World& world,
                                       const std::string& id,
                                       float x, float y,
                                       float resourceAmount) {
    Entity* resource = world.createEntity(id, "resource");

    // ONTOLOGY
    resource->setState("resource_type", std::string("berry_bush"));

    // GEOMETRY
    resource->setState("x", x);
    resource->setState("y", y);

    // DYNAMICS - Regrowth
    resource->setState("amount", resourceAmount);
    resource->setState("max_amount", 100.0f);
    resource->setState("regrowth_rate", 0.1f);  // per tick

    // CONSTRAINT
    resource->setState("active", true);
    resource->setState("min_amount", 0.0f);

    return resource;
}

Entity* EntityTemplates::createPredator(World& world,
                                       const std::string& id,
                                       float x, float y) {
    Entity* predator = world.createEntity(id, "predator");

    // ONTOLOGY
    predator->setState("predator_type", std::string("wolf"));

    // GEOMETRY
    predator->setState("x", x);
    predator->setState("y", y);

    // DYNAMICS
    predator->setState("speed", 1.5f);
    predator->setState("vel_x", 0.0f);
    predator->setState("vel_y", 0.0f);
    predator->setState("attack_damage", 25.0f);

    // CONSTRAINT
    predator->setState("health", 150.0f);
    predator->setState("max_health", 150.0f);
    predator->setState("energy", 100.0f);
    predator->setState("max_energy", 100.0f);
    predator->setState("hunger", 0.0f);

    // EPISTEMIC
    predator->setState("vision_range", 100.0f);
    predator->setState("attack_range", 15.0f);

    return predator;
}

Entity* EntityTemplates::createStructure(World& world,
                                        const std::string& id,
                                        float x, float y,
                                        const std::string& structureType) {
    Entity* structure = world.createEntity(id, "structure");

    // ONTOLOGY
    structure->setState("structure_type", structureType);

    // GEOMETRY
    structure->setState("x", x);
    structure->setState("y", y);
    structure->setState("radius", 20.0f);

    // META - Influence on world
    structure->setState("influence_radius", 50.0f);

    return structure;
}

} // namespace RPE
