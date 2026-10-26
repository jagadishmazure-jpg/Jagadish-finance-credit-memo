"""Brand check: fail if any shipped Markdown or Python file contains
a blocked real-firm name (hashed blocklist, see credit_memo/brand.py).

Usage: python3 tools/brand_check.py [repo_root]
Exits non-zero on the first offending file, listing its path.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from credit_memo.brand import find_blocked  # noqa: E402

SKIP_DIRS = {".git", ".venv", "__pycache__", ".github"}


def main(root: Path) -> int:
    offenders = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix not in (".md", ".py"):
            continue
        if find_blocked(path.read_text(encoding="utf-8", errors="ignore")):
            offenders.append(str(path.relative_to(root)))
    if offenders:
        print("blocked names found in:")
        for offender in offenders:
            print(f"  - {offender}")
        return 1
    print("brand check passed: no blocked names found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")))
