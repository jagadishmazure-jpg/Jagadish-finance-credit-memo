"""Approval gate tests: bypass, reject, absent, low-confidence,
self-contradicting consent, and the happy path -- plus single-use,
named-person, scoped, and expiring enforcement.

These are runtime proofs: each test asserts on the exception (or the
decision) the gate actually raises (or returns), not on source text.
"""

from datetime import datetime, timedelta, timezone

import pytest

from credit_memo.approval import (
    ApprovalAlreadyUsed,
    ApprovalExpired,
    ApprovalGate,
    ApprovalNotFound,
    ApprovalRequired,
    ConsentRejected,
    WrongApprover,
    WrongScope,
    parse_consent,
)
from credit_memo.memo import finalize_memo
from credit_memo.models import Memo


def _memo(memo_id="MEMO-1"):
    return Memo(
        memo_id=memo_id,
        app_ref="APP-TEST",
        status="DRAFT",
        recommendation="Approve",
        risk_band="A - Low risk",
        score=900,
        contributions={},
        policy_results=[],
        kyc_status="PASS",
        conditions=[],
        rationale=[],
    )


def _gate_with_request(memo_id="MEMO-1", approver="Priya Nair", **kw):
    gate = ApprovalGate()
    req = gate.request(memo_id=memo_id, approver=approver, **kw)
    return gate, req


def test_bypass_finalize_without_approval_raises():
    memo = _memo()
    gate = ApprovalGate()
    with pytest.raises(ApprovalRequired):
        finalize_memo(memo, gate, None)
    assert memo.status == "DRAFT"


def test_reject_explicit_no_raises():
    gate, req = _gate_with_request()
    with pytest.raises(ConsentRejected):
        gate.approve(req.token, "Priya Nair", "no, do not approve", 0.95)


def test_absent_unknown_token_raises():
    gate = ApprovalGate()
    with pytest.raises(ApprovalNotFound):
        gate.approve("no-such-token", "Priya Nair", "yes", 0.95)


def test_low_confidence_yes_raises():
    gate, req = _gate_with_request()
    with pytest.raises(ConsentRejected):
        gate.approve(req.token, "Priya Nair", "yes", 0.5)


def test_self_contradicting_consent_raises():
    gate, req = _gate_with_request()
    with pytest.raises(ConsentRejected):
        gate.approve(req.token, "Priya Nair", "yes, wait, no", 0.99)


def test_yes_wait_without_no_is_still_not_clean_consent():
    # "wait" is a negative marker: an affirmative plus a hold is not clean.
    decision, _reason = parse_consent("yes, wait", 0.99)
    assert decision == "reject"


def test_happy_path_finalizes_memo():
    gate, req = _gate_with_request()
    decision = gate.approve(req.token, "Priya Nair", "yes, approved", 0.9)
    memo = finalize_memo(_memo(), gate, decision)
    assert memo.status == "FINAL"
    assert memo.approved_by == "Priya Nair"


def test_single_use_token_cannot_be_reused():
    gate, req = _gate_with_request()
    gate.approve(req.token, "Priya Nair", "yes", 0.9)
    with pytest.raises(ApprovalAlreadyUsed):
        gate.approve(req.token, "Priya Nair", "yes", 0.9)


def test_wrong_person_cannot_approve():
    gate, req = _gate_with_request()
    with pytest.raises(WrongApprover):
        gate.approve(req.token, "Someone Else", "yes", 0.9)


def test_expired_token_raises():
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    gate, req = _gate_with_request(expires_at=past)
    with pytest.raises(ApprovalExpired):
        gate.approve(req.token, "Priya Nair", "yes", 0.9)


def test_decision_scoped_to_one_memo():
    gate, req = _gate_with_request(memo_id="MEMO-1")
    decision = gate.approve(req.token, "Priya Nair", "yes", 0.9)
    with pytest.raises(WrongScope):
        finalize_memo(_memo("MEMO-2"), gate, decision)


def test_confidence_threshold_boundary():
    decision, _ = parse_consent("yes", 0.7)
    assert decision == "accept"
    decision, _ = parse_consent("yes", 0.69)
    assert decision == "reject"


def test_empty_consent_rejected():
    decision, _ = parse_consent("", 0.99)
    assert decision == "reject"
