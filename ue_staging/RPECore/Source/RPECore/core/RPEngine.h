#pragma once

#include "World.h"
#include <memory>
#include <functional>

namespace RPE {

/**
 * RPEngine - The Relational Primitive Engine
 *
 * Implements the deterministic 6-phase update cycle:
 * 1. GEOMETRY - Spatial evaluation, proximity, field gradients
 * 2. CONSTRAINT - Enforce bounds, conservation, validity
 * 3. EPISTEMIC - Determine what entities know
 * 4. DYNAMICS - Apply state changes, movement, interaction
 * 5. META - Structural operations, spawning, rule changes
 * 6. GCO - Global closure, consistency enforcement
 */
class RPEngine {
public:
    RPEngine(World& world);

    // Execute one full tick of the simulation
    void tick();

    // Individual phase execution (for fine-grained control)
    void executeGeometry();
    void executeConstraint();
    void executeEpistemic();
    void executeDynamics();
    void executeMeta();
    void executeGCO();

    // Rule registration
    using RuleFunction = std::function<void(World&)>;

    void registerGeometryRule(const std::string& name, RuleFunction rule);
    void registerConstraintRule(const std::string& name, RuleFunction rule);
    void registerEpistemicRule(const std::string& name, RuleFunction rule);
    void registerDynamicsRule(const std::string& name, RuleFunction rule);
    void registerMetaRule(const std::string& name, RuleFunction rule);

    // Debug/logging
    void setVerbose(bool verbose) { m_verbose = verbose; }

private:
    World& m_world;
    bool m_verbose = false;

    // Rule storage
    std::vector<std::pair<std::string, RuleFunction>> m_geometryRules;
    std::vector<std::pair<std::string, RuleFunction>> m_constraintRules;
    std::vector<std::pair<std::string, RuleFunction>> m_epistemicRules;
    std::vector<std::pair<std::string, RuleFunction>> m_dynamicsRules;
    std::vector<std::pair<std::string, RuleFunction>> m_metaRules;

    void log(const std::string& message) const;
};

} // namespace RPE
