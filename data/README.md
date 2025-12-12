## Data Layout

Follows `referenceGuide.md`:

```
data/
  seeds/
    seed_definitions.jsonl
    seed_translations.jsonl
    seed_repair_examples.jsonl
    seed_evaluator_steps.jsonl
    seed_meta_reasoning.jsonl
  eval/
    rp_eval.jsonl
  archive/
    train_seed.jsonl (deprecated reference)
    train_seed.json (deprecated reference)
  train.jsonl
  test.jsonl
```

Guidance:
- Seeds are canonical and should be loaded first; do not shuffle with train.
- Train/test come from `data/raw/rp_chunks_clean.jsonl` via `scripts/split_rp_chunks.py`.
- Legacy seeds are archived under `data/archive/` for reference only; do not load them.
- Eval files are held out for testing only; do not mix into training.
- Keep schema consistent: `id`, `instruction`, `input`, `output`, `metadata{source,tags,split,difficulty}`.
- Do not merge or auto-augment seed files; add new seeds only with review.
