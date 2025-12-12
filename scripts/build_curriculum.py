#!/usr/bin/env python3
"""
Build a curriculum JSONL by concatenating seeds (ordered) and train, leaving eval separate.

Seeds are loaded in a fixed order and never shuffled.
Train can optionally be shuffled (default: keep original order).
Outputs:
  data/curriculum/train_curriculum.jsonl  (seeds + train)
  data/curriculum/eval_curriculum.jsonl   (copy of eval)
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SEED_FILES = [
    DATA / "seeds" / "seed_definitions.jsonl",
    DATA / "seeds" / "seed_translations.jsonl",
    DATA / "seeds" / "seed_repair_examples.jsonl",
    DATA / "seeds" / "seed_evaluator_steps.jsonl",
    DATA / "seeds" / "seed_meta_reasoning.jsonl",
]

TRAIN_FILE = DATA / "train.jsonl"
EVAL_FILES = [DATA / "eval" / "rp_eval.jsonl"]

OUT_DIR = DATA / "curriculum"
OUT_TRAIN = OUT_DIR / "train_curriculum.jsonl"
OUT_EVAL = OUT_DIR / "eval_curriculum.jsonl"


def load_jsonl(path: Path) -> List[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=True))
            f.write("\n")


def build_curriculum(shuffle_train: bool, seed: int) -> None:
    seeds: List[dict] = []
    for sf in SEED_FILES:
        if not sf.exists():
            raise FileNotFoundError(f"Seed file missing: {sf}")
        seeds.extend(load_jsonl(sf))

    train_rows = load_jsonl(TRAIN_FILE)
    if shuffle_train:
        rng = random.Random(seed)
        rng.shuffle(train_rows)

    curriculum_train = seeds + train_rows
    write_jsonl(OUT_TRAIN, curriculum_train)

    eval_rows: List[dict] = []
    for ef in EVAL_FILES:
        eval_rows.extend(load_jsonl(ef))
    write_jsonl(OUT_EVAL, eval_rows)

    print(f"Wrote {len(curriculum_train)} rows to {OUT_TRAIN}")
    print(f"Wrote {len(eval_rows)} rows to {OUT_EVAL}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build curriculum JSONL files.")
    p.add_argument("--shuffle-train", action="store_true", help="Shuffle train rows (seeds remain ordered).")
    p.add_argument("--seed", type=int, default=42, help="Random seed for train shuffling.")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_curriculum(shuffle_train=args.shuffle_train, seed=args.seed)
