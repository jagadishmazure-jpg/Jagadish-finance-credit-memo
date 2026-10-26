"""PII redaction. The checklist covers card numbers and email addresses
in addition to phone numbers and SSNs -- a card number or an email left
in a memo, a log line, or an error message is a leak, not a detail.

Patterns are applied in an order that avoids misclassification: SSN,
then card numbers, then email, then phone. Redacted output never
contains the original value.
"""

import re

SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_SPACED_RE = re.compile(r"\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b")
CARD_PLAIN_RE = re.compile(r"\b\d{13,19}\b")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)

_PATTERNS = (
    (SSN_RE, "[REDACTED-SSN]"),
    (CARD_SPACED_RE, "[REDACTED-CARD]"),
    (CARD_PLAIN_RE, "[REDACTED-CARD]"),
    (EMAIL_RE, "[REDACTED-EMAIL]"),
    (PHONE_RE, "[REDACTED-PHONE]"),
)


def redact_text(text: str) -> str:
    """Replace every recognised PII pattern with a typed placeholder."""
    out = text
    for pattern, placeholder in _PATTERNS:
        out = pattern.sub(placeholder, out)
    return out


def contains_pii(text: str) -> bool:
    """True if any PII pattern is still present in the text."""
    return any(pattern.search(text) for pattern, _ in _PATTERNS)
