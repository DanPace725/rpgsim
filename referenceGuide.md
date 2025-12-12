
# 📘 **RP-AI Project: Coding Agent Reference Guide**

**Purpose:**
Provide all coding agents with a clear, stable reference for how to work inside this repository.
This document defines goals, constraints, data-architecture decisions, and rules of operation.
Agents must treat these as authoritative unless a human explicitly overrides them.

---

# 1. **Project Overview**

This project develops a small, RP-native language model capable of:

1. Understanding the six Relational Primitives (O, D, G, S, E, M).
2. Producing structured RP-Lang outputs.
3. Detecting and repairing primitive misuse.
4. Performing evaluator-style reasoning (state updates).
5. Translating between natural language and RP-Lang.
6. Applying GCO-style stabilization patterns.
7. Operating within strict curriculum ordering.

The goal is NOT to build a general LLM.
The goal is to build a **domain-specialized, structurally grounded relational reasoner**.

Agents must optimize for conceptual clarity, structural purity, and dataset correctness — not dataset size or convenience.

---

# 2. **Guiding Principles**

Coding agents must follow these principles:

### **2.1 Structural Fidelity First**

Maintain the integrity of:

* RP primitives
* RP-Lang syntax
* evaluator logic
* meta rules
* canonical examples

Never modify core semantics unless explicitly instructed.

### **2.2 Curriculum Stability**

Training proceeds in a layered fashion:

1. **Seed data** (canonical forms)
2. **Simple training data**
3. **Complex training data**
4. **Evaluator/GCO tasks**
5. **Generalization tests**

Do NOT collapse these layers.

### **2.3 Separation of Concerns**

Seed files, training files, and evaluation files must remain separate.
Merging them is unsafe and produces model drift.

### **2.4 Prevent Unauthorized Shortcuts**

Agents must not:

* merge datasets without request
* alter the meaning of primitives
* reformat canonical seeds
* invent new primitives
* collapse decomposition formats
* simplify to non-RP abstractions

### **2.5 Follow RP-Lang Conventions**

Use only the official primitives:

* `ONTOLOGY`
* `DYNAMICS`
* `GEOMETRY`
* `CONSTRAINT`
* `EPISTEMIC`
* `META`

This is the complete set.
Do not create variants (e.g., “ontic”, “spatial”, “motion”, “rules”) unless instructed.

---

# 3. **Data Architecture**

The dataset is organized into three layers.
Agents must respect this structure.

```
data/
  seeds/
      seed_definitions.json
      seed_translations.json
      seed_repair_examples.json
      seed_evaluator_steps.json

  train/
      rp_decomposition.json
      rp_translation_augmented.json
      rp_repair_augmented.json
      rp_engine_reasoning.json
      rp_meta_reasoning.json

  eval/
      rp_primitives_eval.json
      rp_engine_eval.json
      rp_generalization_eval.json
```

### **3.1 Seeds**

Seeds contain:

* minimal definitions
* canonical examples
* clean templates
* correct reasoning patterns

Seeds act as structural anchors.
Do NOT mix with training data.

### **3.2 Training Data**

Training data contains:

* many variations
* scenario-specific examples
* applied reasoning tasks
* evaluator steps
* misuse repair tasks

Training examples must follow formats demonstrated in seeds.

### **3.3 Eval Data**

Evaluation data contains unseen tasks used ONLY for testing.
Agents must NOT modify eval files unless explicitly directed.

---

# 4. **Allowed Transformations**

Agents may:

* add new training examples (following seed patterns)
* expand evaluator-step variants
* expand repair patterns
* generate decomposition/reconstruction tasks
* generate translation tasks
* improve metadata consistency
* add new seed files (only if reviewed)
* create safe augmentation scripts

Agents may NOT:

* alter existing seed content
* change primitive semantics
* flatten curriculum structure
* merge seed + train file contents
* restructure directories without approval

---

# 5. **RP-Lang Format Requirements**

Coding agents writing RP-Lang must follow these rules:

### **5.1 Entity declarations**

Implicit or explicit entity naming is acceptable, e.g.:

```
Entities: Predator p1, Prey q1.
```

### **5.2 Primitive relations**

Each relation must be a clear RP-Lang call:

```
GEOMETRY(p1 near q1, radius=80)
DYNAMICS(q1, flee_target=p1, speed=1.5)
CONSTRAINT(p1, bounds=[10,590])
EPISTEMIC(p1 senses q1, radius=80)
```

### **5.3 Separation of relations**

Relations must be output as a list or multiline block, not embedded prose, unless the format explicitly calls for natural language translation.

---

# 6. **Evaluator / Engine Reasoning Rules**

Evaluator-style tasks must follow this format:

1. Identify relevant relations
2. Determine active triggers (GEOMETRY, EPISTEMIC, META, etc.)
3. Apply CONSTRAINT changes
4. Apply DYNAMICS updates
5. Emit updated states
6. Optional: summarize closure or remaining steps

Example from seeds:

> Step result: GEOMETRY detects proximity.
> CONSTRAINT marks r1 consumed → r1.active=False.
> DYNAMICS on q1… etc.

This structure is mandatory.

---

# 7. **Primitive Misuse Detection**

Agents must detect and correct errors such as:

* using CONSTRAINT for behavior
* using DYNAMICS for boundaries
* confusing GEOMETRY with EPISTEMIC
* using META where ONTOLOGY applies
* missing ONTOLOGY tags
* non-primitive terms

Corrective outputs must:

* state the problem
* provide the corrected relation
* briefly justify the fix

Following the canonical example in seeds.

---

# 8. **Model Training Rules for Agents**

When generating code or training scripts:

### Agents MUST:

* load seeds first
* preserve ordering
* concatenate in final Dataset object, not in file
* balance examples across primitives
* avoid upsampling seeds
* ensure consistent JSON schema

### Agents MUST NOT:

* shuffle seeds with training data
* introduce randomness in curriculum ordering
* auto-augment seeds
* modify canonical formats

---

# 9. **Design Intent Summary (for agents)**

This project builds a **small, principled RP-native intelligence system**, not a general LLM.
Agents should prioritize:

* correctness over creativity
* structure over novelty
* clarity over compression
* curriculum over convenience

The RP framework *is* the architecture.
Training examples must reinforce that.

---

# 10. **Agent Behaviors That Require Human Approval**

Agents must request approval before:

* merging or splitting dataset files
* adding new primitives
* modifying RP-Lang syntax
* altering evaluator logic
* restructuring project directories
* adding new training modes
* introducing automated refactors across seed files

---

# 11. **If Unsure, Ask**

If a coding agent encounters ambiguous instructions or a decision that may violate:

* structural integrity
* curriculum ordering
* primitive semantics
* dataset separations

…it must ask for clarification rather than guess.

---

