# Synthetic lending-policy rulebook

Fictional firm: Tarnfield Community Credit Union.
Document: Synthetic Lending Policy v1.0 (invented for this project).
This rulebook is cited by section in every memo rationale. It is not
any real lender's policy, and no real policy text is reproduced here.

| Rule | Section | Requirement | Severity |
| --- | --- | --- | --- |
| POL-01 | 3.1 | Debt-to-income ratio must not exceed 0.43 | hard |
| POL-02 | 3.2 | Credit score must be at least 620 | hard |
| POL-03 | 3.3 | Loan-to-value ratio must not exceed 0.90 | hard |
| POL-04 | 3.4 | No more than one delinquency in the last 24 months | hard |
| POL-05 | 3.5 | Loan amount must not exceed 500,000 synthetic currency units | hard |
| POL-06 | 3.6 | At least one year of employment or six months of reserves | compensating |

## How severities decide

- A failed **hard** rule forces a Decline recommendation.
- A failed **compensating** rule forces a Refer recommendation (a
  human reviews whether other strengths compensate).
- All rules met, KYC passed, band A or B → Approve (with conditions).

## Worked examples (synthetic)

- APP-2026-003: debt-to-income 0.56 breaches POL-01 → Decline.
- APP-2026-004: employment 0.5 years and reserves 2 months breach
  POL-06 only → Refer.
- APP-2026-005: loan amount 520,000 breaches POL-05 → Decline,
  despite a band-A score.
