"""End-to-end pipeline: the six agents in order.

1. Borrower risk classification (deterministic scorer).
2. Policy compliance checks against the synthetic rulebook.
3. KYC validation.
4. SHAP-style explainability: contributions that sum to the score.
5. Memo synthesis with rulebook-grounded rationales.
6. Named-person approval gate before a memo may become FINAL.

Step costs are synthetic illustrative units, tracked by a Budget that
rejects negative inputs.
"""

from credit_memo.budget import Budget
from credit_memo.kyc import validate_kyc
from credit_memo.memo import build_memo, finalize_memo
from credit_memo.policy import check_policy
from credit_memo.scorer import score_application

STEP_COSTS = {
    "risk": 0.01,
    "policy": 0.01,
    "kyc": 0.02,
    "synthesis": 0.05,
}


def run_pipeline(app, kyc_evidence, memo_id, budget=None):
    """Run agents 1-5 and return a DRAFT memo plus agent outputs."""
    budget = budget or Budget(cap=10.0)
    risk = score_application(app)
    budget.add(STEP_COSTS["risk"])
    policy_results = check_policy(app)
    budget.add(STEP_COSTS["policy"])
    kyc = validate_kyc(kyc_evidence)
    budget.add(STEP_COSTS["kyc"])
    memo = build_memo(app, risk, policy_results, kyc, memo_id)
    budget.add(STEP_COSTS["synthesis"])
    return {
        "memo": memo,
        "risk": risk,
        "policy_results": policy_results,
        "kyc": kyc,
        "budget": budget,
    }


def finalize_with_approval(memo, gate, token, approver, consent_text, confidence):
    """Redeem an approval and mark the memo FINAL. Raises on any gate failure."""
    decision = gate.approve(token, approver, consent_text, confidence)
    return finalize_memo(memo, gate, decision)
