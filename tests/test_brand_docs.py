"""Repo docs must not contain a blocked real-firm name.

Scans every Markdown file shipped in the repo (README, docs/,
knowledge/) with the hashed blocklist. This is the docs-side proof
that the fictional firm is the only firm named.
"""

from pathlib import Path

from credit_memo.brand import find_blocked

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repo_docs_contain_no_blocked_names():
    md_files = [
        p
        for p in REPO_ROOT.rglob("*.md")
        if ".git" not in p.parts and "tests" not in p.parts
    ]
    assert md_files, "no markdown files found to scan"
    offenders = {}
    for path in md_files:
        found = find_blocked(path.read_text(encoding="utf-8"))
        if found:
            offenders[str(path.relative_to(REPO_ROOT))] = found
    assert not offenders, f"blocked names found in docs: {offenders}"
