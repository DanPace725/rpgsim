# RP Data & Rule Engine Overview

## What’s in the repo (current state)
- **Relational primitives**: ONTOLOGY, GEOMETRY, DYNAMICS, CONSTRAINT, EPISTEMIC, META.
- **GCO (Global Closure Operator)**: closure layer that halts relation firing, prunes duplicates, resolves conflicts, commits state, and resets the loop.
- **Data layout**:
  - `data/seeds/` — canonical, ordered seeds (definitions, translations, evaluator steps, repairs, META/GCO reasoning).
  - `data/train.jsonl` / `data/test.jsonl` — tagged chunks from the corpus.
  - `data/eval/` — held-out eval tasks.
  - `data/curriculum/` — `train_curriculum.jsonl` (seeds + train), `eval_curriculum.jsonl` (eval only).
  - `data/processed/` — `train_prompts.jsonl`, `eval_prompts.jsonl` with `{prompt, output}` for training.
- **Scripts**:
  - `scripts/build_curriculum.py` — builds curriculum files.
  - `scripts/preprocess_for_training.py` — builds prompt/target files.
  - `scripts/lint_datasets.py` — schema/tag checks for seeds/eval.

## Core runtime model (abstract)
- **Entities**: `id`, `kind`, `state` map.
- **Relations**: `(id, primitive, source, target, payload)`.
- **Evaluator order**: GEOMETRY → CONSTRAINT → EPISTEMIC → DYNAMICS → META → GCO.
- **GCO**: after a production/event, it stops further firing, dedupes/prunes, enforces constraints, stabilizes ONTOLOGY/state, signals reset.
- **META**: rules-about-rules (spawn, rebuild visibility graphs, enforce schemas, throttle actuation, invoke GCO).

## Using this as a game rule engine (Unreal/C++ oriented)
1) **Data model**: define C++ structs/enums for Entity, Relation, Primitive (the six). Keep handlers per primitive.
2) **World subsystem**: own `FWorld` (entities + relations), tick with the evaluator order above.
3) **GCO layer**: run post-tick to:
   - detect contradictory ONTOLOGY, redundant relations,
   - enforce bounds/constraints,
   - commit/freeze state and emit reset.
4) **META hooks**: listen for events (spawns, lock changes, wall changes) to add/remove relations, rebuild sensing graphs, enforce schemas/safety, and trigger GCO.
5) **Authoring**: express mechanics as relations (movement, bounds, sensing, occlusion, spawn rules). Avoid monolithic scripts; keep rules composable.
6) **Integration**: UE Behavior/State Trees read/write entity state via the subsystem; physics/animation stay native and feed facts back as relations/state.
7) **Performance**: avoid O(n²) by adding spatial indexing for GEOMETRY/EPISTEMIC, and event-driven relation firing where possible.

## How the current data helps
- Seeds show canonical RP/Lang structure, evaluator steps, misuse/repair, and GCO closure patterns.
- Train/test provide broad RP-tagged text for model conditioning.
- Eval provides held-out checks (no training).
- Processed prompts (`data/processed/*.jsonl`) give ready `{prompt, output}` pairs for training a small helper model to propose/fix relations or explain world steps.

## Minimal tick pseudocode (concept)
```
Step() {
  ApplyRelations(Geometry);
  ApplyRelations(Constraint);
  ApplyRelations(Epistemic);
  ApplyRelations(Dynamics);
  ApplyRelations(Meta); // may add/remove relations/entities
  RunGCO();             // dedupe, resolve conflicts, commit, reset
}
```

## Next actions you can take
- Train a small RP helper model on `data/processed/train_prompts.jsonl`; use eval for validation.
- Implement the C++ subsystem with the primitives/evaluator/GCO order above.
- Use seeds as reference tests for the C++ engine (evaluator steps, GCO contradiction/redundancy cases).
