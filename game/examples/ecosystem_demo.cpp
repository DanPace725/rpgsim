/**
 * Ecosystem Demo - v0.01 Prototype
 *
 * A minimal demonstration of the RPE running a simple ecosystem:
 * - A few agents that move and eat
 * - Resource nodes that regrow
 * - Simple energy metabolism
 * - Simple drift (overpopulation -> depletion)
 * - Player can slightly perturb
 *
 * This validates the core RPE concept with real relational primitives.
 */

#include "core/RPEngine.h"
#include "core/World.h"
#include "core/Entity.h"
#include "primitives/EntityTemplates.h"
#include "spatial/SpatialIndex.h"

#include <iostream>
#include <random>
#include <cmath>

using namespace RPE;

// Random number generator
std::random_device rd;
std::mt19937 gen(rd());

// Simple rule: Agents wander randomly when not near food
void wanderBehavior(World& world) {
    std::uniform_real_distribution<float> angleDist(0.0f, 2.0f * 3.14159f);

    for (const auto& [id, entity] : world.getEntities()) {
        if (entity->getKind() != "agent") continue;

        // Random walk
        float angle = angleDist(gen);
        float speed = entity->getState<float>("speed", 1.0f);

        entity->setState("vel_x", std::cos(angle) * speed);
        entity->setState("vel_y", std::sin(angle) * speed);
    }
}

// Simple rule: Find nearby resources
void seekFoodBehavior(World& world) {
    auto* spatialIndex = world.getSpatialIndex();

    for (const auto& [id, entity] : world.getEntities()) {
        if (entity->getKind() != "agent") continue;

        float x = entity->getState<float>("x", 0.0f);
        float y = entity->getState<float>("y", 0.0f);
        float visionRange = entity->getState<float>("vision_range", 80.0f);

        // Query nearby entities
        auto nearby = spatialIndex->queryRadius(Vec2(x, y), visionRange);

        // Find closest resource
        float closestDist = visionRange;
        Vec2 closestPos;
        bool foundFood = false;

        for (const auto& otherId : nearby) {
            if (otherId == id) continue;

            auto* other = world.getEntity(otherId);
            if (!other || other->getKind() != "resource") continue;

            // Check if resource is available
            if (!other->getState<bool>("active", false)) continue;
            if (other->getState<float>("amount", 0.0f) <= 0.0f) continue;

            Vec2 otherPos;
            if (spatialIndex->getPosition(otherId, otherPos)) {
                float dist = Vec2(x, y).distanceTo(otherPos);
                if (dist < closestDist) {
                    closestDist = dist;
                    closestPos = otherPos;
                    foundFood = true;
                }
            }
        }

        // Move toward food if found
        if (foundFood) {
            float dx = closestPos.x - x;
            float dy = closestPos.y - y;
            float dist = std::sqrt(dx * dx + dy * dy);

            if (dist > 0.01f) {
                float speed = entity->getState<float>("speed", 1.0f);
                entity->setState("vel_x", (dx / dist) * speed);
                entity->setState("vel_y", (dy / dist) * speed);
            }
        }
    }
}

// Rule: Apply velocity to position
void applyMovement(World& world) {
    for (const auto& [id, entity] : world.getEntities()) {
        if (!entity->hasState("vel_x") || !entity->hasState("vel_y")) continue;

        float x = entity->getState<float>("x", 0.0f);
        float y = entity->getState<float>("y", 0.0f);
        float vx = entity->getState<float>("vel_x", 0.0f);
        float vy = entity->getState<float>("vel_y", 0.0f);

        entity->setState("x", x + vx);
        entity->setState("y", y + vy);
        world.markEntityDirty(id);
    }
}

// Rule: Consume resources when close
void consumeResources(World& world) {
    auto* spatialIndex = world.getSpatialIndex();

    for (const auto& [id, entity] : world.getEntities()) {
        if (entity->getKind() != "agent") continue;

        float x = entity->getState<float>("x", 0.0f);
        float y = entity->getState<float>("y", 0.0f);
        float consumeRange = 5.0f;

        auto nearby = spatialIndex->queryRadius(Vec2(x, y), consumeRange);

        for (const auto& otherId : nearby) {
            if (otherId == id) continue;

            auto* resource = world.getEntity(otherId);
            if (!resource || resource->getKind() != "resource") continue;

            float amount = resource->getState<float>("amount", 0.0f);
            if (amount <= 0.0f) continue;

            // Consume resource
            float consumed = std::min(amount, 10.0f);
            resource->setState("amount", amount - consumed);

            // Restore agent energy
            float energy = entity->getState<float>("energy", 100.0f);
            float maxEnergy = entity->getState<float>("max_energy", 100.0f);
            entity->setState("energy", std::min(energy + consumed, maxEnergy));

            world.markEntityDirty(id);
            world.markEntityDirty(otherId);
            break;  // Only consume one resource per tick
        }
    }
}

// Rule: Energy metabolism (agents lose energy over time)
void energyMetabolism(World& world) {
    for (const auto& [id, entity] : world.getEntities()) {
        if (entity->getKind() != "agent") continue;

        float energy = entity->getState<float>("energy", 100.0f);
        entity->setState("energy", energy - 0.5f);  // Burn energy per tick

        // Increase hunger
        float hunger = entity->getState<float>("hunger", 0.0f);
        entity->setState("hunger", hunger + 0.1f);

        // Starve if no energy
        if (energy <= 0.0f) {
            float health = entity->getState<float>("health", 100.0f);
            entity->setState("health", health - 5.0f);
        }

        world.markEntityDirty(id);
    }
}

// Rule: Resources regrow over time
void resourceRegrowth(World& world) {
    for (const auto& [id, entity] : world.getEntities()) {
        if (entity->getKind() != "resource") continue;

        float amount = entity->getState<float>("amount", 0.0f);
        float maxAmount = entity->getState<float>("max_amount", 100.0f);
        float regrowthRate = entity->getState<float>("regrowth_rate", 0.1f);

        if (amount < maxAmount) {
            entity->setState("amount", std::min(amount + regrowthRate, maxAmount));
            world.markEntityDirty(id);
        }
    }
}

// Rule: Keep entities in bounds
void boundaryConstraint(World& world) {
    const float minX = 0.0f, maxX = 600.0f;
    const float minY = 0.0f, maxY = 600.0f;

    for (const auto& [id, entity] : world.getEntities()) {
        if (!entity->hasState("x") || !entity->hasState("y")) continue;

        float x = entity->getState<float>("x", 0.0f);
        float y = entity->getState<float>("y", 0.0f);
        bool changed = false;

        if (x < minX) { x = minX; changed = true; }
        if (x > maxX) { x = maxX; changed = true; }
        if (y < minY) { y = minY; changed = true; }
        if (y > maxY) { y = maxY; changed = true; }

        if (changed) {
            entity->setState("x", x);
            entity->setState("y", y);
            world.markEntityDirty(id);
        }
    }
}

int main() {
    std::cout << "=== RPE Ecosystem Demo v0.01 ===" << std::endl;
    std::cout << "Initializing world..." << std::endl;

    // Create world
    World world;
    RPEngine engine(world);
    engine.setVerbose(true);

    // Register rules to the appropriate phases
    engine.registerGeometryRule("SeekFood", seekFoodBehavior);
    engine.registerGeometryRule("Wander", wanderBehavior);

    engine.registerConstraintRule("Boundary", boundaryConstraint);

    engine.registerDynamicsRule("Movement", applyMovement);
    engine.registerDynamicsRule("Consume", consumeResources);
    engine.registerDynamicsRule("Metabolism", energyMetabolism);
    engine.registerDynamicsRule("Regrowth", resourceRegrowth);

    // Create some entities
    std::cout << "Creating entities..." << std::endl;

    // Create 5 agents (herbivores)
    std::uniform_real_distribution<float> posDist(50.0f, 550.0f);
    for (int i = 0; i < 5; ++i) {
        std::string id = "agent_" + std::to_string(i);
        EntityTemplates::createAgent(world, id, posDist(gen), posDist(gen));
    }

    // Create 10 resource nodes
    for (int i = 0; i < 10; ++i) {
        std::string id = "resource_" + std::to_string(i);
        EntityTemplates::createResource(world, id, posDist(gen), posDist(gen), 50.0f);
    }

    std::cout << "Running simulation for 100 ticks..." << std::endl;

    // Run simulation
    for (int tick = 0; tick < 100; ++tick) {
        engine.tick();

        // Print status every 10 ticks
        if (tick % 10 == 0) {
            std::cout << "\n--- Tick " << tick << " ---" << std::endl;

            int aliveAgents = 0;
            float totalEnergy = 0.0f;
            for (const auto& [id, entity] : world.getEntities()) {
                if (entity->getKind() == "agent") {
                    aliveAgents++;
                    totalEnergy += entity->getState<float>("energy", 0.0f);
                }
            }

            std::cout << "Alive agents: " << aliveAgents << std::endl;
            if (aliveAgents > 0) {
                std::cout << "Average energy: " << (totalEnergy / aliveAgents) << std::endl;
            }
        }
    }

    std::cout << "\n=== Simulation Complete ===" << std::endl;
    std::cout << "Final entity count: " << world.getEntities().size() << std::endl;

    return 0;
}
