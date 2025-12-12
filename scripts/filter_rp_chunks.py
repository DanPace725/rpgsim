#!/usr/bin/env python3
"""
Filter noisy RP chunks and emit a cleaned JSONL.

Rules (conservative):
- Drop tiny tokens (len(text.strip()) <= 5)
- Drop emphasis-only labels (e.g., '**Why X:**')
- Drop chunks with no primitive tags and len(text) < 60

Outputs: data/raw/rp_chunks_clean.jsonl
Prints a short summary of removals/kept counts.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Sequence

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "rp_chunks.jsonl"
OUT_PATH = ROOT / "data" / "raw" / "rp_chunks_clean.jsonl"

EMPHASIS_RE = re.compile(r"^\*+[^*]+\*+:?$")  # e.g., **Label:**
HINT_PATTERNS: dict[str, Sequence[str]] = {
    "ONTOLOGY": [r"\bontology", r"\bontological", r"\bidentity", r"\bobject", r"\bentity"],
    "GEOMETRY": [r"\bgeometry", r"\bgeometric", r"\bspatial", r"\bcausal", r"\bcausality", r"\btopolog"],
    "DYNAMICS": [r"\bdynamic", r"\bdynamics", r"\bevolution", r"\binteraction", r"\btransition", r"\bprocess"],
    "CONSTRAINT": [r"\bconstraint", r"\blimit", r"\blimits", r"\bsymmetr", r"\bconservation", r"\blaw"],
    "EPISTEMIC": [r"\bepistemic", r"\binformational", r"\bmeasurement", r"\buncertainty", r"\bobserv"],
    "META": [r"\bmeta", r"\bcross[- ]theory", r"\bfunctor", r"\badjunction", r"\brules about rules"],
}
SOURCE_DEFAULT_TAGS: dict[str, Sequence[str]] = {
    "Relational Primitives/Ecosystem demo.md": ["ONTOLOGY", "GEOMETRY", "DYNAMICS", "CONSTRAINT", "EPISTEMIC", "META"],
    "Relational Primitives/GCO Log Synthesis.md": ["ONTOLOGY", "CONSTRAINT", "META", "DYNAMICS"],
    "Relational Primitives/MRIE.md": ["ONTOLOGY", "EPISTEMIC", "META"],
    "Relational Primitives/Meta-relational Identity exposure (MRIE) Synthesis.md": ["ONTOLOGY", "EPISTEMIC", "META"],
    "Relational Primitives/The Stewardship Architecture A Summary.md": ["CONSTRAINT", "META"],
    "Relational Primitives/Cognitive Signature Capture An Unnamed Threat.md": ["ONTOLOGY", "EPISTEMIC", "META"],
}


def load_rows(path: Path) -> List[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def infer_tags(row: dict) -> List[str]:
    """Infer primitive tags from section/text hints if missing."""
    if row.get("primitive_tags"):
        return row["primitive_tags"]
    defaults = SOURCE_DEFAULT_TAGS.get(row.get("source_path", ""))
    haystack = f"{row.get('section', '')} {row.get('text', '')}".lower()
    tags: List[str] = []
    for name, patterns in HINT_PATTERNS.items():
        if any(re.search(pat, haystack) for pat in patterns):
            tags.append(name)
    if not tags and defaults:
        tags.extend(defaults)
    return sorted(set(tags))


def is_noise(row: dict) -> bool:
    text = row["text"].strip()
    if len(text) <= 5:
        return True
    if EMPHASIS_RE.match(text):
        return True
    if not row.get("primitive_tags") and len(text) < 60:
        return True
    return False


def main() -> None:
    rows = load_rows(RAW_PATH)
    enriched = []
    for r in rows:
        r = dict(r)
        r["primitive_tags"] = infer_tags(r)
        enriched.append(r)
    kept = [r for r in enriched if not is_noise(r)]
    kept = [r for r in kept if r.get("primitive_tags")]  # drop any still tagless
    removed = len(rows) - len(kept)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=True))
            f.write("\n")

    print(f"Input rows:   {len(rows)}")
    print(f"Removed rows: {removed}")
    print(f"Kept rows:    {len(kept)}")
    print(f"Wrote:        {OUT_PATH}")


if __name__ == "__main__":
    main()
