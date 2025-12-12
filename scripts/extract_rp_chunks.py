#!/usr/bin/env python3
"""
Extract RP corpus Markdown into atomic, tagged chunks for fine-tuning datasets.

Outputs JSONL at data/raw/rp_chunks.jsonl with fields:
  - id: stable chunk id
  - source_path: markdown file path
  - section: heading context
  - text: normalized chunk text
  - primitive_tags: list of primitive names inferred from the text
  - start_line / end_line: original line numbers (best-effort)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "data" / "raw" / "rp_chunks.jsonl"

SOURCE_DIR = ROOT / "Relational Primitives"
EXTRA_FILES = [ROOT / "Relational Primitives.md"]

# Primitive detection patterns; keep broad but specific enough to avoid noise.
PRIMITIVE_PATTERNS: Dict[str, Sequence[str]] = {
    "ONTOLOGY": [r"\bontology", r"\bontological", r"\bidentity", r"\bclassification"],
    "GEOMETRY": [r"\bgeometry", r"\bgeometric", r"\bspatial", r"\blayout", r"\bdistance", r"\badjacency", r"\bcontainment"],
    "DYNAMICS": [r"\bdynamics", r"\bdynamic", r"\bchange", r"\bvelocity", r"\bacceleration", r"\benergy", r"\bevolution\b", r"\bmovement"],
    "CONSTRAINT": [r"\bconstraint", r"\bconstraints", r"\blimit", r"\blimits", r"\bclamp", r"\bconservation", r"\bboundary"],
    "EPISTEMIC": [r"\bepistemic", r"\bepistemology", r"\bsensing", r"\bmeasurement", r"\bobserve", r"\bobservation", r"\bvisibility", r"\binformation"],
    "META": [r"\bmeta\b", r"\bmeta-?rel", r"\bmeta[- ]?relation", r"\brules about rules", r"\bhandler", r"\bhandlers"],
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\\[])")


def detect_primitives(text: str) -> List[str]:
    """Return primitive tags found in the text (case-insensitive)."""
    lowered = text.lower()
    tags = []
    for name, patterns in PRIMITIVE_PATTERNS.items():
        if any(re.search(pat, lowered) for pat in patterns):
            tags.append(name)
    return tags


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_into_chunks(text: str, max_len: int = 500) -> List[str]:
    """Split a paragraph into sentence-based chunks within max_len."""
    normalized = normalize_whitespace(text)
    normalized = re.sub(r"^---\s*", "", normalized)
    if not normalized:
        return []

    sentences = SENTENCE_SPLIT.split(normalized)
    # Fallback for text with no clear sentence boundaries.
    if len(sentences) == 1 and len(normalized) > max_len:
        return chunk_by_words(normalized, max_len)

    chunks: List[str] = []
    buffer = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) > max_len:
            if buffer:
                chunks.append(buffer)
                buffer = ""
            chunks.extend(chunk_by_words(sentence, max_len))
            continue
        if not buffer:
            buffer = sentence
            continue
        if len(buffer) + 1 + len(sentence) <= max_len:
            buffer = f"{buffer} {sentence}"
        else:
            chunks.append(buffer)
            buffer = sentence
    if buffer:
        chunks.append(buffer)
    return chunks


def chunk_by_words(text: str, max_len: int) -> List[str]:
    """Simple word-based chunking for very long runs with no punctuation."""
    words = text.split()
    chunks: List[str] = []
    buffer_words: List[str] = []
    length = 0
    for word in words:
        projected = length + (1 if buffer_words else 0) + len(word)
        if projected > max_len and buffer_words:
            chunks.append(" ".join(buffer_words))
            buffer_words = [word]
            length = len(word)
        else:
            buffer_words.append(word)
            length = projected
    if buffer_words:
        chunks.append(" ".join(buffer_words))
    return chunks


def iter_paragraphs_with_context(path: Path) -> Iterable[Dict[str, object]]:
    heading_stack: List[str] = []
    paragraph_lines: List[str] = []
    start_line = 1

    def flush(current_line: int) -> Iterable[Dict[str, object]]:
        nonlocal paragraph_lines
        if not paragraph_lines:
            return []
        paragraph = "\n".join(paragraph_lines).strip()
        paragraph_lines = []
        if not paragraph or re.match(r"^-{3,}$", paragraph):
            return []

        section = " > ".join(heading_stack)
        chunks = split_into_chunks(paragraph)
        results = []
        for chunk in chunks:
            results.append(
                {
                    "section": section,
                    "text": chunk,
                    "start_line": start_line,
                    "end_line": current_line,
                }
            )
        return results

    current_line = 0
    for current_line, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.rstrip("\n")
        heading_match = re.match(r"^(#+)\s*(.*)", line)
        if heading_match:
            yield from flush(current_line - 1)
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            heading_stack = heading_stack[: level - 1] + [title]
            start_line = current_line + 1
            continue

        if not line.strip():
            yield from flush(current_line)
            start_line = current_line + 1
            continue

        if not paragraph_lines:
            start_line = current_line
        paragraph_lines.append(line)

    yield from flush(current_line)


def collect_sources() -> List[Path]:
    sources = []
    if SOURCE_DIR.exists():
        sources.extend(sorted(SOURCE_DIR.glob("*.md")))
    for extra in EXTRA_FILES:
        if extra.exists():
            sources.append(extra)
    return sources


def extract_chunks() -> List[Dict[str, object]]:
    chunks: List[Dict[str, object]] = []
    for source in collect_sources():
        for idx, para in enumerate(iter_paragraphs_with_context(source)):
            chunk = {
                "id": f"{source.stem}:{idx:04d}",
                "source_path": str(source.relative_to(ROOT)),
                "section": para["section"],
                "text": para["text"],
                "primitive_tags": detect_primitives(para["text"]),
                "start_line": para["start_line"],
                "end_line": para["end_line"],
            }
            chunks.append(chunk)
    return chunks


def main() -> None:
    chunks = extract_chunks()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=True))
            f.write("\n")
    print(f"Wrote {len(chunks)} chunks to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
