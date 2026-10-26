"""8-word overlap check: fail if any 8 consecutive words in the repo's
docs also appear, in order, in the source text.

The source text itself is NEVER committed to this repo. Pass the path
to an extracted source text file (e.g. from pdftotext) as argv[1] and
the repo root as argv[2]. Normalisation: lowercase, ligature repair,
punctuation stripped, whitespace collapsed -- so a match means a real
copied phrase, not a formatting coincidence.

Usage: python3 tools/overlap_check.py <source_txt> [repo_root]
"""

import re
import sys
from pathlib import Path

LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl"}


def normalise(text: str) -> list:
    for lig, repl in LIGATURES.items():
        text = text.replace(lig, repl)
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return text.split()


def windows(words, n=8):
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def main(source_path: Path, root: Path) -> int:
    source_windows = windows(normalise(source_path.read_text(encoding="utf-8", errors="ignore")))
    hits = {}
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        doc_windows = windows(normalise(path.read_text(encoding="utf-8", errors="ignore")))
        overlap = sorted(doc_windows & source_windows)
        if overlap:
            hits[str(path.relative_to(root))] = overlap
    if hits:
        print("8-word overlap hits found:")
        for path, phrases in hits.items():
            for phrase in phrases:
                print(f"  {path}: {phrase!r}")
        return 1
    print("8-word overlap check passed: 0 hits")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: overlap_check.py <source_txt> [repo_root]")
        raise SystemExit(2)
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    raise SystemExit(main(Path(sys.argv[1]), root))
