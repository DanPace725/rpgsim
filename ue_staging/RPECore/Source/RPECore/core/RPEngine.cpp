#include "core/RPEngine.h"
#include "spatial/SpatialIndex.h"
#include <iostream>

namespace RPE {

RPEngine::RPEngine(World &world) : m_world(world), m_verbose(false) {}

void RPEngine::tick() {
  log("=== RPE Tick " + std::to_string(m_world.getCurrentTick()) + " ===");

  // Execute the 6-phase update cycle in strict order
  executeGeometry();
  executeConstraint();
  executeEpistemic();
  executeDynamics();
  executeMeta();
  executeGCO();

  // Clear dirty flags and increment tick
  m_world.clearDirtyFlags();
  m_world.incrementTick();
}

void RPEngine::executeGeometry() {
  log("Phase 1: GEOMETRY");

  // Execute all registered geometry rules
  for (const auto &[name, rule] : m_geometryRules) {
    log("  Running: " + name);
    rule(m_world);
  }

  // Built-in: Update spatial index for all entities with position
  auto &entities = m_world.getEntities();
  auto *spatialIndex = m_world.getSpatialIndex();

  for (const auto &[id, entity] : entities) {
    if (entity->hasState("x") && entity->hasState("y")) {
      float x = entity->getState<float>("x", 0.0f);
      float y = entity->getState<float>("y", 0.0f);
      spatialIndex->updatePosition(id, Vec2(x, y));
    }
  }
}

void RPEngine::executeConstraint() {
  log("Phase 2: CONSTRAINT");

  // Execute all registered constraint rules
  for (const auto &[name, rule] : m_constraintRules) {
    log("  Running: " + name);
    rule(m_world);
  }

  // Built-in: Clamp health/energy values, enforce bounds
  auto &entities = m_world.getEntities();
  for (const auto &[id, entity] : entities) {
    // Clamp health between 0 and max_health
    if (entity->hasState("health")) {
      float health = entity->getState<float>("health", 0.0f);
      float maxHealth = entity->getState<float>("max_health", 100.0f);
      if (health < 0.0f) {
        entity->setState("health", 0.0f);
        m_world.markEntityDirty(id);
      } else if (health > maxHealth) {
        entity->setState("health", maxHealth);
        m_world.markEntityDirty(id);
      }
    }

    // Clamp energy between 0 and max_energy
    if (entity->hasState("energy")) {
      float energy = entity->getState<float>("energy", 0.0f);
      float maxEnergy = entity->getState<float>("max_energy", 100.0f);
      if (energy < 0.0f) {
        entity->setState("energy", 0.0f);
        m_world.markEntityDirty(id);
      } else if (energy > maxEnergy) {
        entity->setState("energy", maxEnergy);
        m_world.markEntityDirty(id);
      }
    }
  }
}

void RPEngine::executeEpistemic() {
  log("Phase 3: EPISTEMIC");

  // Execute all registered epistemic rules
  for (const auto &[name, rule] : m_epistemicRules) {
    log("  Running: " + name);
    rule(m_world);
  }
}

void RPEngine::executeDynamics() {
  log("Phase 4: DYNAMICS");

  // Execute all registered dynamics rules
  for (const auto &[name, rule] : m_dynamicsRules) {
    log("  Running: " + name);
    rule(m_world);
  }
}

void RPEngine::executeMeta() {
  log("Phase 5: META");

  // Execute all registered meta rules
  for (const auto &[name, rule] : m_metaRules) {
    log("  Running: " + name);
    rule(m_world);
  }

  // Built-in: Remove entities with health <= 0
  auto &entities = m_world.getEntities();
  std::vector<std::string> toRemove;

  for (const auto &[id, entity] : entities) {
    if (entity->hasState("health")) {
      float health = entity->getState<float>("health", 0.0f);
      if (health <= 0.0f) {
        toRemove.push_back(id);
      }
    }
  }

  for (const auto &id : toRemove) {
    log("  Removing dead entity: " + id);
    m_world.removeEntity(id);
  }
}

void RPEngine::executeGCO() {
  log("Phase 6: GCO (Global Closure)");

  // The GCO ensures world consistency
  // For now, this is a placeholder for:
  // - Deduplicating relations
  // - Resolving contradictions
  // - Enforcing schema-level invariants
  // - Collapsing equivalences

  // This will be expanded as we add more complex rules
}

void RPEngine::registerGeometryRule(const std::string &name,
                                    RuleFunction rule) {
  m_geometryRules.emplace_back(name, rule);
}

void RPEngine::registerConstraintRule(const std::string &name,
                                      RuleFunction rule) {
  m_constraintRules.emplace_back(name, rule);
}

void RPEngine::registerEpistemicRule(const std::string &name,
                                     RuleFunction rule) {
  m_epistemicRules.emplace_back(name, rule);
}

void RPEngine::registerDynamicsRule(const std::string &name,
                                    RuleFunction rule) {
  m_dynamicsRules.emplace_back(name, rule);
}

void RPEngine::registerMetaRule(const std::string &name, RuleFunction rule) {
  m_metaRules.emplace_back(name, rule);
}

void RPEngine::log(const std::string &message) const {
  if (m_verbose) {
    std::cout << message << std::endl;
  }
}

} // namespace RPE
