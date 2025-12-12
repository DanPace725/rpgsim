#!/usr/bin/env python3
"""
Preprocess curriculum JSONL into a simple prompt/target JSONL for training.

Reads:
  data/curriculum/train_curriculum.jsonl
  data/curriculum/eval_curriculum.jsonl

Outputs:
  data/processed/train_prompts.jsonl
  data/processed/eval_prompts.jsonl

Transform:
- prompt = instruction + optional blank line + input (if non-empty)
- target = output
- metadata, id are dropped (kept only if --keep-metadata is set)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
CURR_DIR = ROOT / "data" / "curriculum"
OUT_DIR = ROOT / "data" / "processed"


def load_jsonl(path: Path) -> List[Dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def make_prompt(instruction: str, input_text: str) -> str:
    instruction = instruction.strip()
    input_text = input_text.strip() if input_text else ""
    if input_text:
        return f"{instruction}\n\n{input_text}"
    return instruction


def transform(rows: List[Dict], keep_metadata: bool) -> List[Dict]:
    out = []
    for r in rows:
        prompt = make_prompt(r.get("instruction", ""), r.get("input", ""))
        item = {"prompt": prompt, "output": r.get("output", "")}
        if keep_metadata:
            item["metadata"] = r.get("metadata", {})
            item["id"] = r.get("id")
        out.append(item)
    return out


def write_jsonl(path: Path, rows: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=True))
            f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess curriculum into prompt/target pairs.")
    parser.add_argument("--keep-metadata", action="store_true", help="Keep metadata/id in output.")
    args = parser.parse_args()

    train_rows = load_jsonl(CURR_DIR / "train_curriculum.jsonl")
    eval_rows = load_jsonl(CURR_DIR / "eval_curriculum.jsonl")

    train_out = transform(train_rows, keep_metadata=args.keep_metadata)
    eval_out = transform(eval_rows, keep_metadata=args.keep_metadata)

    write_jsonl(OUT_DIR / "train_prompts.jsonl", train_out)
    write_jsonl(OUT_DIR / "eval_prompts.jsonl", eval_out)

    print(f"Wrote {len(train_out)} rows to {OUT_DIR / 'train_prompts.jsonl'}")
    print(f"Wrote {len(eval_out)} rows to {OUT_DIR / 'eval_prompts.jsonl'}")


if __name__ == "__main__":
    main()
