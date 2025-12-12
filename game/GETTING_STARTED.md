# Getting Started with "A World That Lives"

Welcome! This guide will help you understand and start working with the RPE-based simulation game.

## 📋 Quick Start Checklist

- [ ] Read this document
- [ ] Review `README.md` for project overview
- [ ] Read `docs/RELATIONAL_PRIMITIVES.md` to understand the core concepts
- [ ] Install build tools (see `BUILD.md`)
- [ ] Build the project
- [ ] Run `ecosystem_demo`
- [ ] Experiment with modifying rules
- [ ] Start building your own entities/behaviors

## 🎯 What You're Building

This isn't a traditional game. It's a **living simulation** where:

- ❌ No quest scripts
- ❌ No behavior trees
- ❌ No spawn tables
- ❌ No level triggers

Instead:

- ✅ Entities have relationships
- ✅ Behavior emerges from rules
- ✅ World has metabolism
- ✅ Time matters
- ✅ Everything adapts

## 🧩 Core Components

### 1. Entity (include/core/Entity.h)

An entity is anything that exists in the world:
- Creatures (agents, predators)
- Resources (food, minerals)
- Structures (buildings, machines)
- Abstract (factions, cultures)

**Key Concept:** Entities have **state** (properties) but minimal logic. Logic lives in **relations** and **rules**.

### 2. Relation (include/core/Relation.h)

A relation describes how entities relate via one of six primitives:
- ONTOLOGY - what it is
- GEOMETRY - where/when it is
- CONSTRAINT - what limits it
- EPISTEMIC - what it knows
- DYNAMICS - how it changes
- META - how it affects structure

**Key Concept:** Relations replace most traditional "methods" on entities.

### 3. World (include/core/World.h)

The world holds:
- All entities
- All relations
- Spatial index (for geometry queries)
- Dirty tracking (for efficient updates)

**Key Concept:** World is a pure data container. It doesn't "run" anything - that's the engine's job.

### 4. RPEngine (include/core/RPEngine.h)

The engine executes the 6-phase tick:
1. GEOMETRY - update spatial relationships
2. CONSTRAINT - enforce bounds
3. EPISTEMIC - update knowledge
4. DYNAMICS - apply changes
5. META - structural operations
6. GCO - ensure consistency

**Key Concept:** Deterministic order ensures debuggable, reproducible behavior.

## 🔬 Understanding the Demo

The `ecosystem_demo` is the v0.01 prototype. Let's break it down:

### Entities Created
```cpp
// 5 herbivore agents
EntityTemplates::createAgent(world, "agent_0", x, y);

// 10 resource nodes
EntityTemplates::createResource(world, "resource_0", x, y, 50.0f);
```

### Rules Registered

**Geometry Phase:**
- `SeekFood` - agents look for nearby resources
- `Wander` - agents move randomly when no food visible

**Constraint Phase:**
- `Boundary` - keep entities in world bounds

**Dynamics Phase:**
- `Movement` - apply velocity to position
- `Consume` - agents eat nearby resources
- `Metabolism` - agents lose energy over time
- `Regrowth` - resources regenerate

**Meta Phase:**
- Built-in: remove dead entities (health <= 0)

### Emergent Patterns to Watch For

After running the demo, you should observe:

1. **Clustering** - Agents group near resource-rich areas
2. **Boom/Bust** - Population spikes then crashes from starvation
3. **Migration** - Agents move between depleted and fresh areas
4. **Resource Zones** - Some areas become "dead zones"

**None of this is scripted.** It emerges from:
- Energy metabolism (dynamics)
- Food seeking (geometry + epistemic)
- Resource regeneration (dynamics)
- Death from starvation (meta)

## 🛠️ Making Your First Modification

### Goal: Make agents move faster when hungry

1. **Open** `examples/ecosystem_demo.cpp`

2. **Find** the `seekFoodBehavior` function

3. **Modify** speed based on hunger:

```cpp
void seekFoodBehavior(World& world) {
    auto* spatialIndex = world.getSpatialIndex();

    for (const auto& [id, entity] : world.getEntities()) {
        if (entity->getKind() != "agent") continue;

        // NEW: Check hunger level
        float hunger = entity->getState<float>("hunger", 0.0f);
        float baseSpeed = entity->getState<float>("speed", 1.0f);

        // Increase speed when hungry
        float speedMultiplier = 1.0f + (hunger * 0.01f);

        float x = entity->getState<float>("x", 0.0f);
        float y = entity->getState<float>("y", 0.0f);
        float visionRange = entity->getState<float>("vision_range", 80.0f);

        auto nearby = spatialIndex->queryRadius(Vec2(x, y), visionRange);

        // ... find closest food ...

        if (foundFood) {
            float dx = closestPos.x - x;
            float dy = closestPos.y - y;
            float dist = std::sqrt(dx * dx + dy * dy);

            if (dist > 0.01f) {
                // NEW: Use modified speed
                float effectiveSpeed = baseSpeed * speedMultiplier;
                entity->setState("vel_x", (dx / dist) * effectiveSpeed);
                entity->setState("vel_y", (dy / dist) * effectiveSpeed);
            }
        }
    }
}
```

4. **Rebuild** and run

5. **Observe:** Agents now desperately sprint when starving!

This is emergent behavior modification - you changed one rule, and the entire ecosystem adapts.

## 🎨 Creating Your Own Entity Type

### Goal: Add a "water source" that entities need

1. **Create template** in `include/primitives/EntityTemplates.h`:

```cpp
static Entity* createWaterSource(World& world,
                                 const std::string& id,
                                 float x, float y);
```

2. **Implement** in `src/primitives/EntityTemplates.cpp`:

```cpp
Entity* EntityTemplates::createWaterSource(World& world,
                                          const std::string& id,
                                          float x, float y) {
    Entity* water = world.createEntity(id, "water_source");

    water->setState("x", x);
    water->setState("y", y);
    water->setState("water_amount", 100.0f);
    water->setState("refill_rate", 0.5f);

    return water;
}
```

3. **Add thirst** to agents in `EntityTemplates::createAgent`:

```cpp
agent->setState("thirst", 0.0f);
agent->setState("max_thirst", 100.0f);
```

4. **Add rule** to increase thirst in `ecosystem_demo.cpp`:

```cpp
void thirstIncrease(World& world) {
    for (const auto& [id, entity] : world.getEntities()) {
        if (entity->getKind() != "agent") continue;

        float thirst = entity->getState<float>("thirst", 0.0f);
        entity->setState("thirst", thirst + 0.2f);  // Faster than hunger

        // Damage if too thirsty
        if (thirst > 80.0f) {
            float health = entity->getState<float>("health");
            entity->setState("health", health - 2.0f);
        }
    }
}

// Register it
engine.registerDynamicsRule("Thirst", thirstIncrease);
```

5. **Add seeking behavior** for water (similar to food)

6. **Observe:** Now agents must balance food AND water. New patterns emerge:
   - Agents die if they focus only on food
   - Water sources become gathering points
   - Migration patterns change

## 📚 Next Steps

### Beginner
- [ ] Modify existing rules (speed, metabolism rate, vision range)
- [ ] Add new entity types (predators, different resources)
- [ ] Change world size or entity counts
- [ ] Add debug printing to understand flow

### Intermediate
- [ ] Implement predator-prey dynamics
- [ ] Add simple reproduction (split when energy high)
- [ ] Create "safe zones" that repel predators
- [ ] Implement day/night cycle (affects behavior)

### Advanced
- [ ] Build faction system (groups with shared knowledge)
- [ ] Implement player-built structures (affect world rules)
- [ ] Add cultural memory (factions remember locations)
- [ ] Create emergent trade (resource exchange)

## 🐛 Troubleshooting

### "All agents die immediately"
- **Cause:** Metabolism too harsh or resources too scarce
- **Fix:** Reduce `energyMetabolism` rate or increase initial resources

### "Agents don't find food"
- **Cause:** Vision range too small or resources too far
- **Fix:** Increase `vision_range` or spawn more resources

### "Simulation seems stuck"
- **Cause:** No dynamics rules registered
- **Fix:** Ensure rules are registered with `engine.registerDynamicsRule(...)`

### "Build fails"
- **Cause:** Missing compiler or CMake
- **Fix:** See `BUILD.md` for installation instructions

## 💡 Design Philosophy

When adding features, ask:

1. **Which primitive does this belong to?**
   - Identity → ONTOLOGY
   - Location → GEOMETRY
   - Limits → CONSTRAINT
   - Knowledge → EPISTEMIC
   - Change → DYNAMICS
   - Structure → META

2. **Can it emerge from existing rules?**
   - Don't add explicit "flocking" code - let it emerge from proximity
   - Don't script "predator avoidance" - let it emerge from energy cost vs. threat

3. **Does it respect epistemic bounds?**
   - Entities can only act on what they KNOW
   - No omniscient AI
   - No instant global knowledge

4. **Is it deterministic?**
   - Same inputs → same outputs
   - Randomness is fine, but seed it for reproducibility
   - Debug by replaying ticks

## 📖 Recommended Reading Order

1. `README.md` - Project overview
2. `docs/RELATIONAL_PRIMITIVES.md` - Core concepts (YOU ARE HERE)
3. `BUILD.md` - How to compile
4. `examples/ecosystem_demo.cpp` - Working example
5. `rpe.md` - Technical specification
6. `rpgsimoverview.md` - Long-term vision

## 🤝 Getting Help

When stuck:

1. **Enable verbose mode:**
   ```cpp
   engine.setVerbose(true);
   ```

2. **Add debug prints:**
   ```cpp
   std::cout << "Agent " << id << " energy: " << energy << std::endl;
   ```

3. **Check relations:**
   ```cpp
   auto rels = world.getRelationsForEntity(id);
   for (auto* r : rels) std::cout << r->toString() << std::endl;
   ```

4. **Verify phase order** - Is your rule in the right phase?

5. **Test in isolation** - Create minimal world with 1-2 entities

---

**Welcome to a world that lives.**

**The world doesn't wait for you. It doesn't revolve around you.**

**But it will remember you were here.**
