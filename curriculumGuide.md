---

# 📘 **RP Curriculum Generator Specification (with GCO Integration)**

**Authoritative Instructions for Coding Agents**

This document defines how to generate **seed**, **training**, and **evaluation** data for building a model that reasons using the Relational Primitives (RP) and the Global Closure Operator (GCO).
Coding agents must follow this document **exactly**, without modification, unless a human explicitly overrides it.

---

# 1. **Purpose of the Curriculum**

The curriculum trains a small RP-native model to:

* Understand all six Relational Primitives (O, D, G, S, E, M)
* Apply the Global Closure Operator (GCO)
* Perform evaluator-style reasoning
* Detect and repair primitive misuse
* Translate between natural language and RP-Lang
* Maintain relational and closure consistency
* Produce minimal, stable, canonical relational structures
* Avoid inventing new primitives or breaking RP semantics

The model must learn **not just RP syntax**, but the **dynamics, stability rules, and closure logic** that make RP reasoning coherent.

---

# 2. **Dataset Structure**

The curriculum consists of four tiers plus a seed layer.
Coding agents must respect this structure.

```
Seeds/
Tier 1 – Single-Primitive & Basic Reasoning
Tier 2 – Multi-Primitive Decomposition & Reconstruction
Tier 3 – Evaluator Logic, Multi-Step Reasoning, GCO Application
Tier 4 – META-Level Rules, GCO-Driven Governance, Compositionality
Eval/ – Held-out test sets (never used for training)
```

Each tier builds on the previous one.
**Do not mix seeds and training data.**
**Do not generate Tier 3 or Tier 4 examples until Tier 1 and Tier 2 are sufficiently populated.**

---

# 3. **Seed Layer (Canonical Patterns Only)**

Seeds define the **grammar**, **format**, and **minimal patterns** the model must internalize.

Seed files include:

### ✔ Primitive Definitions

(from `seed_definitions.json`)

### ✔ Primitive Misuse Repairs

(from `seed_repair_examples.json`)

### ✔ Evaluator Step Patterns

(from `seed_evaluator_steps.json`)

### ✔ Translation Patterns

(from `seed_translations.json`)

### ✔ META Reasoning Seeds

(from `seed_meta_reasoning.json`)

### ✔ **GCO Seeds (required)**

Coding agents must generate additional seeds that define:

1. **What GCO is**
2. **How GCO detects contradictions**
3. **How GCO prunes redundant relations**
4. **How GCO identifies fixed points**
5. **How GCO signals that reasoning is complete**
6. **How GCO interacts with META rules**

Example GCO seed patterns:

```
Instruction: Apply GCO to reach closure.
Input:
  ONTOLOGY(a, kind=Prey)
  ONTOLOGY(a, kind=Predator)
Output:
  GCO: contradictory identity assignments. Closure requires a consistent ONTOLOGY. Choose one or flag for META resolution.
```

```
Instruction: Show whether the relational set is already in closure.
Input:
  GEOMETRY(a near b, radius=10)
  DYNAMICS(a, speed=1)
Output:
  Set is in closure: no contradictions, no redundant relations, no unresolved dependencies.
```

Seed GCO examples must be **minimal, unambiguous, and canonical**.

---

# 4. **Tier Specifications (Now Including GCO Requirements)**

## **Tier 1 — Single Primitive + Simple Reasoning**

Coding agents generate examples that:

* use **one** primitive (or a simple pair)
* demonstrate correct structure
* identify primitive misuse
* translate natural language ↔ RP-Lang
* stay minimal

**GCO is not applied in Tier 1.**
If a closure question arises, mark the example for a higher tier.

---

## **Tier 2 — Multi-Primitive Decomposition & Reconstruction**

Task types:

* Full decomposition into O/D/G/S/E/M
* Reconstruction of narratives into RP-Lang
* Multi-primitive misuse detection and repair
* Structural consistency tasks

**Tier 2 introduces GCO awareness**, but not execution.

Examples may ask:

* “Is this relational set complete?”
* “Which relations violate closure?”
* “Which contradictions must be resolved before closure?”

Agents must not:

* perform evaluator loops
* compute dynamic updates
* apply full GCO reasoning (reserved for Tier 3)

---

## **Tier 3 — Evaluator Reasoning + GCO Application**

This tier introduces full **Evaluator Loop + GCO** tasks:

1. GEOMETRY triggers
2. EPISTEMIC gates
3. CONSTRAINT clamps
4. DYNAMICS updates state
5. META modifies relations
6. **GCO checks for closure or unresolved contradictions**

Allowed task types:

* Single-step evaluator + closure check
* Multi-step evaluator until closure
* Apply GCO to simplify relational sets
* Show how GCO detects contradictions
* Show how GCO prunes redundant relations
* Check if a stable state is reached

**Tier 3 is where the model learns to reason like a simulation engine.**

Coding agents must strictly enforce:

* proper ordering
* explicit state changes
* explicit closure results

**Examples MAY NOT invent new evaluator mechanics.**
Evaluator logic must match the seeds.

---

## **Tier 4 — META-Level & GCO-Governed Compositionality**

This tier teaches:

* META as rules-about-rules
* META as schema enforcer
* META as closure stabilizer
* GCO as the final arbitration layer
* High-level governance logic
* Structural constraints across multiple relational clusters

Allowed task types:

* META rules that enforce closure
* META rules that resolve contradictions
* META rules that rebuild visibility (epistemic) graphs
* META rules that enforce schemas
* META rules that validate world structure using GCO
* GCO detecting global fixed points across RP sets

Tier 4 must show **why** and **how** GCO ensures system integrity.

---

# 5. **Formatting Rules for All Generated Examples**

Coding agents must produce JSON of this form:

```json
{
  "id": "tierX/example-id",
  "instruction": "...",
  "input": "...",
  "output": "...",
  "metadata": {
    "tier": "X",
    "tags": ["..."],
    "difficulty": "...",
    "source": "Constructed"
  }
}
```

Rules:

* IDs must be unique
* tier must match the actual example
* tags must describe primitives used
* output must be minimal and structurally correct

---

# 6. **GCO Rules Coding Agents Must Follow**

When generating examples:

### ✔ GCO **may**:

* prune contradictions
* reduce redundancy
* detect fixed points
* signal closure
* resolve ambiguous relational sets
* require META to intervene

### ✔ GCO **must not**:

* invent new primitives
* perform dynamics
* perform geometry
* apply constraints
* replace evaluator logic

GCO operates **after** evaluator logic, not instead of it.

### ✔ GCO outputs must state:

* whether closure is achieved
* what contradictions exist
* what minimal canonical form remains

---

# 7. **Prohibited Behaviors**

Coding agents may NOT:

* modify seed examples
* merge seeds and training files
* invent primitives
* change RP-Lang syntax
* add new evaluator mechanics
* collapse GCO into ad hoc reasoning
* produce long-winded narrative outputs
* introduce hidden state or probabilistic behavior outside DYNAMICS

---

# 8. **How Coding Agents Generate Curriculum Data**

Whenever asked to generate training examples, coding agents must:

1. Identify the target **tier**
2. Follow the rules for that tier
3. Apply GCO logic only where allowed
4. Produce minimal, canonical JSON
5. Verify structural correctness before output
6. Include all required metadata
7. Keep all examples internally consistent with the seed layer

If unsure, **ask for clarification rather than guessing**.

---

# 9. **Master Instruction Template (Use This in Every Prompt to Coding Agents)**

When giving a generation request, wrap your instruction like this:

---

### ✔ **INSTRUCTION FOR THE CODING AGENT:**

> You are the RP Curriculum Generator.
> You must follow the **RP Curriculum Generator Specification (with GCO Integration)**.
> Your goal is to create training examples for the specified tier.
> Follow all rules regarding:
> • RP primitives
> • evaluator logic
> • GCO
> • example formatting
> • constraints and invariants
> • seed preservation
> • tier boundaries
>
> Do not invent primitives.
> Do not alter GCO mechanics.
> Do not mix tiers.
> Do not change RP semantics.
>
> Output only valid JSON in the required schema.

---

Then add a task, e.g.:

```
Generate 15 Tier 3 evaluator + GCO examples.
```

or:

```
Generate 10 Tier 2 decomposition examples involving epistemic + geometry.
```

---

