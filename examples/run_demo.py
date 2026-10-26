"""Demo: run the full pipeline over the five synthetic samples and
print each memo's headline plus its exact contribution breakdown.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from credit_memo.approval import ApprovalGate  # noqa: E402
from credit_memo.pipeline import finalize_with_approval, run_pipeline  # noqa: E402
from credit_memo.samples import CLEAN_KYC, SAMPLES  # noqa: E402


def main():
    gate = ApprovalGate()
    for app in SAMPLES:
        result = run_pipeline(app, CLEAN_KYC, f"MEMO-{app.app_ref}")
        memo = result["memo"]
        risk = result["risk"]
        print(f"== {app.app_ref}: {memo.recommendation} "
              f"(band {risk.band}, score {risk.score})")
        for feature, points in sorted(risk.contributions.items()):
            print(f"   {feature}: {points:+d}")
        print(f"   sum check: {risk.base_score} + "
              f"{sum(risk.contributions.values())} = {risk.score}")
        print(f"   policy: "
              f"{sum(1 for r in result['policy_results'] if r.passed)}/"
              f"{len(result['policy_results'])} rules met, "
              f"KYC {result['kyc'].status}")
    # Finalize the first memo through the approval gate.
    result = run_pipeline(SAMPLES[0], CLEAN_KYC, "MEMO-FINAL-DEMO")
    req = gate.request(memo_id="MEMO-FINAL-DEMO", approver="Priya Nair")
    final = finalize_with_approval(
        result["memo"], gate, req.token, "Priya Nair", "yes, approved", 0.9
    )
    print(f"== MEMO-FINAL-DEMO: status {final.status}, "
          f"approved by {final.approved_by}")


if __name__ == "__main__":
    main()
