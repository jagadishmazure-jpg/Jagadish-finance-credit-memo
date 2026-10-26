"""Named-person approval gate (agent 6, human oversight).

Rules, all enforced and all tested:
- Approvals name one person. A different person cannot use them.
- Approvals are single-use: a token works once, then it is spent.
- Approvals are scoped: a token approves exactly one memo.
- Approvals expire: a token past its expiry is dead.
- Consent must be an unambiguous, high-confidence "yes". A low-confidence
  "yes", an explicit "no", no approval at all, and a self-contradicting
  consent such as "yes, wait, no" are all rejected -- each by its own
  test, because a gate that only handles the happy path is decoration.
"""

import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

CONFIDENCE_THRESHOLD = 0.7

_AFFIRMATIVE = {"yes", "approve", "approved", "confirm", "confirmed", "accept"}
_NEGATIVE = {
    "no",
    "not",
    "never",
    "stop",
    "cancel",
    "reject",
    "refuse",
    "wait",
    "hold",
    "don't",
    "dont",
}


class ApprovalError(Exception):
    pass


class ApprovalNotFound(ApprovalError):
    pass


class ApprovalExpired(ApprovalError):
    pass


class ApprovalAlreadyUsed(ApprovalError):
    pass


class WrongApprover(ApprovalError):
    pass


class WrongScope(ApprovalError):
    pass


class ConsentRejected(ApprovalError):
    pass


class ApprovalRequired(ApprovalError):
    pass


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z']+", text.lower()))


def parse_consent(text: str, confidence: float) -> tuple:
    """Return ("accept", reason) or ("reject", reason).

    Accepts only an unambiguous affirmative at or above the confidence
    threshold. Anything else -- including a message that contains both
    affirmative and negative markers -- is a rejection.
    """
    if not isinstance(confidence, (int, float)) or confidence != confidence:
        return ("reject", "confidence is not a number")
    words = _tokens(text or "")
    affirmative = bool(words & _AFFIRMATIVE)
    negative = bool(words & _NEGATIVE)
    if affirmative and negative:
        return ("reject", "self-contradicting consent")
    if negative:
        return ("reject", "explicit refusal")
    if not affirmative:
        return ("reject", "no affirmative consent found")
    if confidence < CONFIDENCE_THRESHOLD:
        return ("reject", "confidence below threshold")
    return ("accept", "unambiguous affirmative consent at sufficient confidence")


@dataclass
class ApprovalRequest:
    token: str
    memo_id: str
    approver: str
    scope: str
    created_at: datetime
    expires_at: datetime
    used: bool = False


@dataclass
class ApprovalDecision:
    token: str
    memo_id: str
    approver: str
    accepted: bool
    reason: str


class ApprovalGate:
    """Issues and redeems named-person, single-use, scoped, expiring approvals."""

    def __init__(self):
        self._requests: dict = {}

    def request(
        self,
        memo_id: str,
        approver: str,
        scope: str | None = None,
        ttl_minutes: int = 60,
        expires_at: datetime | None = None,
    ) -> ApprovalRequest:
        now = datetime.now(timezone.utc)
        req = ApprovalRequest(
            token=secrets.token_hex(16),
            memo_id=memo_id,
            approver=approver,
            scope=scope or memo_id,
            created_at=now,
            expires_at=expires_at or (now + timedelta(minutes=ttl_minutes)),
        )
        self._requests[req.token] = req
        return req

    def approve(
        self,
        token: str,
        approver: str,
        consent_text: str,
        confidence: float,
    ) -> ApprovalDecision:
        req = self._requests.get(token)
        if req is None:
            raise ApprovalNotFound("no approval request matches this token")
        if req.approver != approver:
            raise WrongApprover("approval names a different person")
        if req.used:
            raise ApprovalAlreadyUsed("approval token has already been used")
        if datetime.now(timezone.utc) > req.expires_at:
            raise ApprovalExpired("approval token has expired")
        decision, reason = parse_consent(consent_text, confidence)
        if decision != "accept":
            raise ConsentRejected(f"consent rejected: {reason}")
        req.used = True
        return ApprovalDecision(
            token=token,
            memo_id=req.memo_id,
            approver=approver,
            accepted=True,
            reason=reason,
        )

    def require_final(self, memo, decision: ApprovalDecision | None) -> None:
        """Raise unless a valid approval decision covers this memo."""
        if decision is None or not decision.accepted:
            raise ApprovalRequired("no approval decision supplied for this memo")
        if decision.memo_id != memo.memo_id:
            raise WrongScope("approval decision covers a different memo")
