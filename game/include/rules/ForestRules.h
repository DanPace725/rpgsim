#pragma once

#include "core/RPEngine.h"
#include "core/World.h"
#include <iostream>
#include <algorithm>
#include <cmath>

namespace ForestRules {

// --- DYNAMICS RULES ---

// 1. Photosynthesis: Producers gain energy from Sun influence
void Photosynthesis(RPE::World& world) {
    const auto& relations = world.getRelationsByPrimitive(RPE::Primitive::DYNAMICS);
    
    for (const auto* relation : relations) {
        if (relation->getRelationType() != "influence") continue;
        if (relation->getSource() != "sun") continue;
        
        // Sun -> Target (Producer)
        auto targetId = relation->getTarget();
        if (!targetId) continue;
        
        auto* producer = world.getEntity(*targetId);
        if (!producer) continue;

        // Check if it's a producer
        if (producer->getKind() != "producer") continue;

        // Apply energy gain based on weight and P2_dynamics
        double weight = 1.0;
        if (auto p = relation->getPayload<double>()) weight = *p;
        
        // Get entity's dynamic receptivity (P2)
        double p2 = producer->getState<double>("P2_dynamics", 0.5);
        
        double currentEnergy = producer->getState<double>("energy", 0.0);
        double maxEnergy = producer->getState<double>("max_energy", 100.0);
        
        // Growth formula: Base * Weight * Receptivity
        double energyGain = 5.0 * weight * p2; 
        
        producer->setState("energy", std::min(currentEnergy + energyGain, maxEnergy));
        world.markEntityDirty(*targetId);
    }
}

// 2. Predation/consumption: Consumers eat resources or other entities
void Consumption(RPE::World& world) {
    const auto& relations = world.getRelationsByPrimitive(RPE::Primitive::DYNAMICS);

    for (const auto* relation : relations) {
        if (relation->getRelationType() != "influence") continue;
        
        auto sourceId = relation->getSource(); // The Resource/Prey
        auto targetId = relation->getTarget(); // The Consumer (Reverse of influence flow in JSON? JSON says "acorns" -> "squirrel" influence. So Resource impacts Consumer)
        
        // Note: In the JSON, "acorns" influence "squirrel". This means existence of acorns prevents squirrel starvation.
        // We interpret this as: Squirrel can eat Acorns.
        
        if (!targetId) continue;
        
        auto* resource = world.getEntity(sourceId);
        auto* consumer = world.getEntity(*targetId);
        
        if (!resource || !consumer) continue;
        
        // Only consumers/predators eat
        std::string consumerType = consumer->getKind();
        if (consumerType != "consumer" && consumerType != "predator" && consumerType != "apex") continue;

        double weight = 0.5;
        if (auto p = relation->getPayload<double>()) weight = *p;

        // Attempt to eat
        double consumerEnergy = consumer->getState<double>("energy", 0.0);
        double maxEnergy = consumer->getState<double>("max_energy", 100.0);
        
        if (consumerEnergy >= maxEnergy) continue; // Full

        // Amount available?
        // If it's a 'resource' kind, it has 'amount'.
        // If it's a 'consumer' kind (prey), it has 'population' or 'energy'.
        
        double eatAmount = 0.0;
        
        if (resource->getKind() == "resource" || resource->getKind() == "water") {
            double amount = resource->getState<double>("amount", 0.0);
            if (amount > 0) {
                eatAmount = std::min(amount, 2.0 * weight); // Eat small amount
                resource->setState("amount", amount - eatAmount);
            }
        } else {
            // Predation (eating population)
            double pop = resource->getState<double>("population", 0.0);
            if (pop > 0) {
                eatAmount = std::min(pop, 0.5 * weight); // Kill some prey
                resource->setState("population", pop - eatAmount);
            }
        }
        
        if (eatAmount > 0) {
            consumer->setState("energy", std::min(consumerEnergy + eatAmount * 5.0, maxEnergy));
            world.markEntityDirty(sourceId);
            world.markEntityDirty(*targetId);
        }
    }
}

// 3. Metabolic Decay: Living things lose energy
void MetabolicDecay(RPE::World& world) {
    for (const auto& [id, entity] : world.getEntities()) {
        std::string kind = entity->getKind();
        if (kind == "producer" || kind == "consumer" || kind == "predator" || kind == "apex") {
            double energy = entity->getState<double>("energy", 0.0);
            double decay = 1.0; // Base decay
            
            // Dynamics P2 affects metabolism (higher dynamics = faster burn?)
            double p2 = entity->getState<double>("P2_dynamics", 0.5);
            decay *= (1.0 + p2);
            
            entity->setState("energy", std::max(0.0, energy - decay));
            world.markEntityDirty(id);
        }
    }
}

// 4. Population Dynamics based on Energy
void PopulationDynamics(RPE::World& world) {
    for (const auto& [id, entity] : world.getEntities()) {
        if (entity->hasState("population") && entity->hasState("energy")) {
            double pop = entity->getState<double>("population", 0.0);
            double energy = entity->getState<double>("energy", 0.0);
            
            if (energy > 80.0) {
                // Resize: grow population
                entity->setState("population", pop * 1.05);
                entity->setState("energy", energy - 20.0); // Cost of reproduction
                world.markEntityDirty(id);
            } else if (energy < 10.0) {
                // Starvation
                entity->setState("population", pop * 0.90);
                world.markEntityDirty(id);
            }
        }
    }
}

void RegisterForestRules(RPE::RPEngine& engine) {
    // Dynamics
    engine.registerDynamicsRule("Photosynthesis", Photosynthesis);
    engine.registerDynamicsRule("Consumption", Consumption);
    engine.registerDynamicsRule("MetabolicDecay", MetabolicDecay);
    engine.registerDynamicsRule("Population", PopulationDynamics);
}

} // namespace ForestRules
