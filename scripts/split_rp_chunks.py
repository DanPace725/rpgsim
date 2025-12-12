#!/usr/bin/env python3
"""
Split the cleaned RP chunks into train/test JSONL files.

Strategy:
- Start from data/raw/rp_chunks_clean.jsonl (all tagged).
- Shuffle with a fixed seed.
- Reserve 20% for test.

Outputs:
- data/train.jsonl
- data/test.jsonl
Each line carries the original fields.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "raw" / "rp_chunks_clean.jsonl"
TRAIN_OUT = ROOT / "data" / "train.jsonl"
TEST_OUT = ROOT / "data" / "test.jsonl"
TEST_FRACTION = 0.2
SEED = 42


def load_rows(path: Path) -> List[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def main() -> None:
    rows = load_rows(INPUT)
    random.seed(SEED)
    random.shuffle(rows)

    split = int(len(rows) * (1 - TEST_FRACTION))
    train, test = rows[:split], rows[split:]

    TRAIN_OUT.parent.mkdir(parents=True, exist_ok=True)
    with TRAIN_OUT.open("w", encoding="utf-8") as f:
        for r in train:
            f.write(json.dumps(r, ensure_ascii=True))
            f.write("\n")
    with TEST_OUT.open("w", encoding="utf-8") as f:
        for r in test:
            f.write(json.dumps(r, ensure_ascii=True))
            f.write("\n")

    print(f"Total: {len(rows)} | Train: {len(train)} | Test: {len(test)}")


if __name__ == "__main__":
    main()
