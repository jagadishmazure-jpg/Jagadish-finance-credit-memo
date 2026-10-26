"""Memo synthesis and end-to-end pipeline tests."""

from credit_memo.approval import ApprovalGate
from credit_memo.kyc import validate_kyc
from credit_memo.memo import build_memo
from credit_memo.pipeline import finalize_with_approval, run_pipeline
from credit_memo.policy import RULES, check_policy
from credit_memo.samples import CLEAN_KYC, FAILED_KYC, SAMPLES
from credit_memo.scorer import score_application


def test_memo_starts_as_draft():
    app = SAMPLES[0]
    memo = build_memo(
        app, score_application(app), check_policy(app), validate_kyc(CLEAN_KYC), "M1"
    )
    assert memo.status == "DRAFT"
    assert memo.recommendation == "Approve"


def test_memo_rationale_cites_every_rule():
    app = SAMPLES[0]
    memo = build_memo(
        app, score_application(app), check_policy(app), validate_kyc(CLEAN_KYC), "M1"
    )
    joined = "\n".join(memo.rationale)
    for rule in RULES:
        assert rule["rule_id"] in joined
        assert rule["section"] in joined


def test_memo_contributions_sum_line_is_exact():
    app = SAMPLES[0]
    risk = score_application(app)
    memo = build_memo(app, risk, check_policy(app), validate_kyc(CLEAN_KYC), "M1")
    assert memo.contributions == risk.contributions
    assert memo.score == risk.base_score + sum(risk.contributions.values())


def test_recommendation_matrix_across_samples():
    expected = {
        "APP-2026-001": "Approve",
        "APP-2026-002": "Approve",
        "APP-2026-003": "Decline",
        "APP-2026-004": "Refer",
        "APP-2026-005": "Decline",
    }
    for app in SAMPLES:
        memo = build_memo(
            app,
            score_application(app),
            check_policy(app),
            validate_kyc(CLEAN_KYC),
            f"MEMO-{app.app_ref}",
        )
        assert memo.recommendation == expected[app.app_ref], app.app_ref


def test_failed_kyc_forces_decline():
    app = SAMPLES[0]
    memo = build_memo(
        app, score_application(app), check_policy(app), validate_kyc(FAILED_KYC), "M1"
    )
    assert memo.recommendation == "Decline"
    assert memo.kyc_status == "FAIL"


def test_pipeline_end_to_end_finalizes_with_approval():
    result = run_pipeline(SAMPLES[0], CLEAN_KYC, "MEMO-E2E")
    assert result["memo"].status == "DRAFT"
    assert abs(result["budget"].spent - 0.09) < 1e-9
    gate = ApprovalGate()
    req = gate.request(memo_id="MEMO-E2E", approver="Priya Nair")
    final = finalize_with_approval(
        result["memo"], gate, req.token, "Priya Nair", "yes, approved", 0.9
    )
    assert final.status == "FINAL"
    assert final.approved_by == "Priya Nair"


def test_sample_data_carries_no_pii():
    for app in SAMPLES:
        assert app.borrower_name is None
        assert app.borrower_email is None
        assert app.borrower_ssn is None
        assert app.borrower_phone is None
        assert app.borrower_card is None
    refs = [a.app_ref for a in SAMPLES]
    assert len(refs) == len(set(refs))
