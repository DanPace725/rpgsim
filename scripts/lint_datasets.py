#!/usr/bin/env python3
"""
Lint seeds/eval JSONL files for schema and RP tagging consistency.

Checks:
- Required fields: id, instruction, input, output, metadata
- metadata fields: source, tags (non-empty list), split, difficulty
- split is one of: seed/train/test/eval
- text length minimums (instruction/output >= 10 chars)
- primitive presence: at least one primitive tag (primitive_tags or metadata tags that include a primitive)

Note: train/test files are raw chunks and intentionally skipped here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MIN_TEXT_LEN = 10
PRIMITIVES = {"ONTOLOGY", "GEOMETRY", "DYNAMICS", "CONSTRAINT", "EPISTEMIC", "META"}
SPLITS = {"seed", "train", "test", "eval"}


def load_jsonl(path: Path) -> List[dict]:
    # Explicit UTF-8 prevents Windows default cp1252 decode errors.
    text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def has_primitive(row: dict) -> bool:
    metas = {t.upper() for t in row.get("metadata", {}).get("tags", [])}
    prim_tags = set(row.get("primitive_tags", []))
    return bool(PRIMITIVES & (metas | prim_tags))


def lint_file(path: Path) -> List[str]:
    errors: List[str] = []
    rows = load_jsonl(path)
    for idx, r in enumerate(rows):
        loc = f"{path}:{idx}"
        for field in ("id", "instruction", "output", "metadata"):
            if field not in r:
                errors.append(f"{loc} missing field {field}")
        if "instruction" in r and len(r["instruction"].strip()) < MIN_TEXT_LEN:
            errors.append(f"{loc} instruction too short")
        if "output" in r and len(r["output"].strip()) < MIN_TEXT_LEN:
            errors.append(f"{loc} output too short")
        md = r.get("metadata", {})
        for field in ("source", "tags", "split", "difficulty"):
            if field not in md:
                errors.append(f"{loc} metadata missing {field}")
        if "split" in md and md.get("split") not in SPLITS:
            errors.append(f"{loc} invalid split {md.get('split')}")
        if "tags" in md and (not isinstance(md["tags"], list) or not md["tags"]):
            errors.append(f"{loc} metadata.tags empty or not list")
        if not has_primitive(r):
            errors.append(f"{loc} no primitive tag found")
    return errors


def main() -> None:
    paths = list((DATA_DIR / "seeds").glob("*.jsonl")) + list((DATA_DIR / "eval").glob("*.jsonl"))
    all_errors: List[Tuple[Path, str]] = []
    for p in paths:
        errs = lint_file(p)
        for e in errs:
            all_errors.append((p, e))
    if all_errors:
        print("Lint errors:")
        for _, e in all_errors:
            print(e)
    else:
        print("All files passed lint.")


if __name__ == "__main__":
    main()
