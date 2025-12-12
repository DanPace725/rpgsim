# A World That Lives - RPG Simulation Game

A living, adaptive simulation world where everything—ecology, factions, culture, machines, stories—emerges from **Relational Primitives** rather than scripts.

## 🎯 Core Concept

This is a sandbox RPG-simulation where:
- The world has a **metabolism**, not a spawn table
- Entities behave based on **relationships**, not state machines
- Time and entropy shape everything
- Factions behave like **alive, evolving cultures**
- The world gradually **learns the player's style** and adapts
- Creations become **real entities** in the simulation
- Narratives **grow organically** instead of being authored

## 🧬 Technical Foundation: The Relational Primitive Engine (RPE)

The engine is built on six relational primitives derived from first principles:

1. **ONTOLOGY** - What entities are (identity, structure, composition)
2. **GEOMETRY** - Where/when entities exist (spatial, causal structure)
3. **CONSTRAINT** - Rules that govern (bounds, limits, conservation)
4. **EPISTEMIC** - What can be known (visibility, memory, inference)
5. **DYNAMICS** - How entities change (movement, interaction, transformation)
6. **META** - Rules about rules (spawning, structural changes)

### The 6-Phase Deterministic Tick

Each simulation tick executes in strict order:

1. **GEOMETRY** - Spatial evaluation, proximity, field gradients
2. **CONSTRAINT** - Enforce bounds, conservation, validity
3. **EPISTEMIC** - Determine what entities know
4. **DYNAMICS** - Apply state changes, movement, interaction
5. **META** - Structural operations, spawning, rule changes
6. **GCO** - Global Closure Operator ensures consistency

## 🏗️ Project Structure

```
game/
├── include/
│   ├── core/
│   │   ├── Entity.h          # Entity representation
│   │   ├── Relation.h        # Relational primitives
│   │   ├── World.h           # World state container
│   │   └── RPEngine.h        # 6-phase tick engine
│   ├── spatial/
│   │   └── SpatialIndex.h    # Spatial acceleration structure
│   └── primitives/
│       └── EntityTemplates.h # Entity factory templates
├── src/                      # Implementation files
├── examples/
│   └── ecosystem_demo.cpp    # v0.01 prototype demo
├── tests/                    # Unit tests (future)
└── CMakeLists.txt           # Build configuration
```

## 🚀 Building the Project

### Requirements
- CMake 3.15 or higher
- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)

### Build Instructions

```bash
# Create build directory
mkdir build
cd build

# Configure
cmake ..

# Build
cmake --build .

# Run the demo
./ecosystem_demo  # Linux/Mac
ecosystem_demo.exe  # Windows
```

## 🌱 Current Status: v0.01 Prototype

The current prototype demonstrates:

✅ **Core RPE Architecture**
- 6-phase deterministic tick system
- Entity and relation graph
- Spatial indexing for geometry queries

✅ **Basic Ecosystem**
- Agents that move and seek food
- Resource nodes that regrow
- Simple energy metabolism
- Overpopulation → depletion dynamics

✅ **Real Relational Primitives**
- Not faked or scripted
- Genuine emergence from RP framework
- Debuggable and transparent

### Running the Ecosystem Demo

The `ecosystem_demo` executable creates a tiny biome with:
- 5 herbivore agents
- 10 resource nodes (berry bushes)
- 600x600 world space

Agents:
- Wander randomly when not hungry
- Seek nearby food when hungry
- Consume resources to restore energy
- Lose energy over time (metabolism)
- Die if energy reaches zero

Resources:
- Get depleted when consumed
- Regrow slowly over time
- Provide energy to agents

Watch for emergent patterns:
- Clustering around resource-rich areas
- Population booms and crashes
- Migration patterns
- Resource depletion zones

## 🎮 Roadmap

### v0.1 Goals
- [ ] Basic faction seeds (competing groups)
- [ ] Meaningful construction (player-built structures)
- [ ] World memory (remembers past states)
- [ ] Player behavior learning
- [ ] Simple cultural drift
- [ ] Enhanced epistemic system (stealth, rumors)

### v0.2 Goals
- [ ] Multiple biomes
- [ ] Predator-prey dynamics
- [ ] Trade and resource exchange
- [ ] Emergent narrative events
- [ ] Visualization layer (2D renderer)

### Long-term Vision
- True emergence at scale
- Worlds with unique identity
- Factions with real culture
- Player creations as ontological objects
- Time as a real mechanic
- Adaptive world that learns player style

## 📚 Design Principles

Following the RP framework means:

1. **Structural Fidelity First** - Maintain integrity of the six primitives
2. **No Scripted Behavior** - Everything emerges from relational rules
3. **Deterministic Updates** - Same inputs → same outputs (debuggable)
4. **Separation of Concerns** - Each primitive has a distinct role
5. **Change-Driven Evaluation** - Only process dirty entities
6. **Epistemic Grounding** - Entities can only act on what they know

## 🧪 Testing the Concepts

The prototype validates:

✓ Relational primitives are sufficient for basic AI
✓ 6-phase tick produces coherent behavior
✓ GCO maintains world consistency
✓ Spatial indexing scales to hundreds of entities
✓ Emergent patterns arise without scripting
✓ System is debuggable and transparent

## 📖 Further Reading

See the project documentation:
- `rpe.md` - Relational Primitive Engine specification
- `rpgsimoverview.md` - High-level game design
- `Relational Primitives/` - Theoretical foundation

## 🤝 Contributing

This is an experimental research project exploring emergent simulation design. Contributions that maintain structural fidelity to the RP framework are welcome.

## 📄 License

[To be determined]

---

**The world does not exist for you. It does not revolve around you.**

**Your presence stabilizes some systems, destabilizes others, and shifts the flow of meaning.**

**Your story is the story of how the world changes because you exist inside it.**
