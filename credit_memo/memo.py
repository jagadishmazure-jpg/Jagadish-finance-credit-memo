"""Memo synthesis layer (agent 5).

Builds a structured, human-readable credit memo from the other agents'
outputs. Rationales cite rulebook sections, never vibes. The finished
text is passed through PII redaction as a final sweep, and the builder
only ever reads the application's reference and numeric fields -- PII
fields are not referenced here at all.
"""

from credit_memo.models import Memo
from credit_memo.policy import RULEBOOK_TITLE, compensating_failures, hard_failures
from credit_memo.redaction import redact_text


def recommend(risk, policy_results, kyc) -> tuple:
    """Return (recommendation, conditions). Deterministic, rule-driven."""
    conditions = []
    if kyc.status != "PASS":
        return "Decline", ["KYC must pass before any approval can proceed."]
    if hard_failures(policy_results):
        return "Decline", ["A hard policy rule failed; see cited rules."]
    if risk.band.startswith("D"):
        return "Decline", ["Risk band D requires decline under this policy."]
    if compensating_failures(policy_results):
        conditions.append("Compensating-factor rule not met: manual review required.")
        return "Refer", conditions
    if risk.band.startswith("C"):
        return "Refer", ["Elevated risk band: senior review required."]
    if risk.contributions.get("loan_to_value", 0) <= 60:
        conditions.append("Standard closing conditions apply.")
    else:
        conditions.append("Loan-to-value above 0.80: confirm insurance requirements.")
    return "Approve", conditions


def build_memo(app, risk, policy_results, kyc, memo_id: str) -> Memo:
    recommendation, conditions = recommend(risk, policy_results, kyc)
    rationale = []
    rationale.append(
        f"Risk band {risk.band} with score {risk.score} "
        f"(base {risk.base_score} plus feature contributions)."
    )
    for feature, points in sorted(risk.contributions.items()):
        direction = "added" if points >= 0 else "subtracted"
        rationale.append(f"Feature {feature} {direction} {abs(points)} points.")
    for result in policy_results:
        verdict = "met" if result.passed else "not met"
        rationale.append(
            f"Rule {result.rule_id} ({RULEBOOK_TITLE} section {result.section}): "
            f"{result.title} -- {verdict}."
        )
    rationale.append(f"KYC validation: {kyc.status}.")
    if kyc.blockers:
        rationale.append(f"KYC blockers: {', '.join(kyc.blockers)}.")
    rationale.append(f"Recommendation: {recommendation}.")

    lines = [
        "CREDIT MEMO -- SYNTHETIC DATA ONLY",
        f"Memo: {memo_id}",
        f"Application: {app.app_ref}",
        f"Recommendation: {recommendation}",
        f"Risk band: {risk.band} (score {risk.score})",
        "",
        "Feature contributions (SHAP-style, sum to score minus base):",
    ]
    for feature, points in sorted(risk.contributions.items()):
        lines.append(f"  - {feature}: {points:+d}")
    lines.append(f"  Sum check: {risk.base_score} + "
                 f"{sum(risk.contributions.values())} = {risk.score}")
    lines.append("")
    lines.append("Policy compliance (synthetic rulebook):")
    for result in policy_results:
        mark = "PASS" if result.passed else "FAIL"
        lines.append(
            f"  - [{mark}] {result.rule_id} section {result.section}: "
            f"{result.title}"
        )
    lines.append("")
    lines.append(f"KYC: {kyc.status}")
    lines.append("")
    lines.append("Conditions:")
    for condition in conditions:
        lines.append(f"  - {condition}")
    lines.append("")
    lines.append("Rationale:")
    for item in rationale:
        lines.append(f"  - {item}")
    lines.append("")
    lines.append(
        "This memo is generated from synthetic data for demonstration only. "
        "It is not a lending decision and requires human review."
    )
    text = redact_text("\n".join(lines))
    return Memo(
        memo_id=memo_id,
        app_ref=app.app_ref,
        status="DRAFT",
        recommendation=recommendation,
        risk_band=risk.band,
        score=risk.score,
        contributions=dict(risk.contributions),
        policy_results=list(policy_results),
        kyc_status=kyc.status,
        conditions=list(conditions),
        rationale=rationale,
        text=text,
    )


def finalize_memo(memo: Memo, gate, decision) -> Memo:
    """Mark a memo FINAL only after the approval gate accepts a decision."""
    gate.require_final(memo, decision)
    memo.status = "FINAL"
    memo.approved_by = decision.approver
    memo.approval_token = decision.token
    return memo
