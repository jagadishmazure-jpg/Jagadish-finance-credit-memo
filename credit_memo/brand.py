"""Brand/name guard.

The blocklist is stored as SHA-256 hashes, never as plain names, so
the guard itself cannot leak the names it blocks. Checking works the
other way round: the text under inspection is normalised, split into
word n-grams (1-4 words), and each n-gram is hashed and compared with
the blocklist. A match means a real firm's name appears in the text.

The blocklist covers real financial firms and one real company name
that must never appear as the fictional firm in this repo, plus the
rejected candidate firm name. The fictional firm used throughout this
repo is Tarnfield Community Credit Union, which is invented.
"""

import hashlib
import re

# SHA-256 hashes of blocked real-firm names (lowercase, single spaces).
BLOCKLIST_HASHES = {
    "e1fb683f7236ee085c65a00a8d9bcd5a5501fc0b4ab6aaf652fad9b4141e39f6",
    "197bdb02c68031ce816c4b840a43faed15cc73ea2bb36a477f8e64eb24264d9f",
    "311ff2d71234e230eb559f843c1f5c548302246a365221713da47017e656e672",
    "2cbb9e58bf3bcbdfe805a2aebb57f84531b114a18e5f0e6377d9f5a7bf86576b",
    "309e31536dcf1556bb6c81b00cd992445b79ad8e89f9c0cd2a1f0675342538b3",
    "3b8eccd79c406969d8fa1a98deea4b0a3d13df5959d6ea421b99222a64055246",
    "0c356331e8aaea73d1833d9eb370a48df65827302d65374418599b510c42feed",
    "7105a46cb4c2810f0c916e0bb4b4e4ef834ad42040c471b42c96d356a9fd1b21",
    "67b51232d90eef075f44549519a721f50e31cfe58c93c9c30132291aac942601",
    "066b5b5ad80702e14f11863bf5c6e976c2fa01e830f80320905d50fd99f155ed",
    "97c683ed108f54b3c154179a4f6a9361b2c890e2b45837f79b9fe6374769c26f",
    "078946f817adfe58c51a3bfde4639bd01682b88e13742ab3d46117b1eeb80fbc",
    "3a72c8e8fec7c5b7efd55cdc0946f7684258d41a07b2ffdf070b31ee4bb19b02",
    "d4bc5a5c67f1008a065b84e5fcb6e5e226d146966b9e3db8323daae237561f5b",
    "4b1f6f530975ef68d8f30d663efe02fb1e20ca2fdde8c5416ecfeb21fb881e96",
    "6228a5824a1e8d1554519125795ad14c1b7be681c6e9efbbbc66c91bbf2f89e5",
}

# Runtime extensions (e.g. a deployer adding their own blocked names).
_EXTRA_HASHES = set()


def _hash(phrase: str) -> str:
    return hashlib.sha256(phrase.encode("utf-8")).hexdigest()


def add_blocked_name(name: str) -> None:
    """Add a name to the blocklist (stored as its hash only)."""
    _EXTRA_HASHES.add(_hash(" ".join(name.lower().split())))


def _ngrams(words, size):
    return (" ".join(words[i : i + size]) for i in range(len(words) - size + 1))


def find_blocked(text: str) -> list:
    """Return the list of blocked-name hashes found in the text."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    blocked = set(BLOCKLIST_HASHES) | _EXTRA_HASHES
    found = []
    for size in (1, 2, 3, 4):
        for gram in _ngrams(words, size):
            digest = _hash(gram)
            if digest in blocked:
                found.append(digest)
    return sorted(set(found))


def check_text(text: str) -> bool:
    """True when the text contains no blocked real-firm name."""
    return not find_blocked(text)
