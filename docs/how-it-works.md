# How it works, step by step

## Run the demo

```bash
python3 examples/run_demo.py
```

The demo runs all five synthetic samples through the pipeline and
finalises one memo through the approval gate. Expected headlines:

| Application | Recommendation | Band | Score | Policy |
| --- | --- | --- | --- | --- |
| APP-2026-001 | Approve | A - Low risk | 960 | 6/6 |
| APP-2026-002 | Approve | B - Moderate risk | 700 | 6/6 |
| APP-2026-003 | Decline | D - High risk | 180 | 5/6 |
| APP-2026-004 | Refer | A - Low risk | 790 | 5/6 |
| APP-2026-005 | Decline | A - Low risk | 780 | 5/6 |

Two rows deserve attention. APP-2026-004 has a strong score but
fails the compensating-factor rule (short employment, thin reserves),
so it is referred, not approved. APP-2026-005 has a strong score but
breaches a hard policy rule (loan amount above the synthetic cap),
so it is declined. Score never overrides policy here.

## Run one application yourself

```python
from credit_memo.kyc import validate_kyc
from credit_memo.memo import build_memo, finalize_memo
from credit_memo.models import Application, KycEvidence
from credit_memo.policy import check_policy
from credit_memo.scorer import score_application
from credit_memo.approval import ApprovalGate

app = Application(
    app_ref="APP-DEMO",
    annual_income=120000, monthly_debt=2000, loan_amount=240000,
    property_value=320000, credit_score=760, delinquencies_24m=0,
    employment_years=6, reserves_months=8,
)
evidence = KycEvidence(True, True, True, True)
memo = build_memo(app, score_application(app), check_policy(app),
                  validate_kyc(evidence), "MEMO-DEMO")
print(memo.status)  # DRAFT

gate = ApprovalGate()
req = gate.request(memo_id="MEMO-DEMO", approver="Priya Nair")
decision = gate.approve(req.token, "Priya Nair", "yes, approved", 0.9)
finalize_memo(memo, gate, decision)
print(memo.status)  # FINAL
```

## Recommendation logic

1. KYC FAIL → Decline.
2. Any hard policy failure → Decline.
3. Risk band D → Decline.
4. Any compensating failure → Refer.
5. Risk band C → Refer.
6. Otherwise → Approve, with conditions (for example, an
   insurance-requirements check when loan-to-value is above 0.80).
