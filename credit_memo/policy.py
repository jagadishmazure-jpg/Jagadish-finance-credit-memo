"""Synthetic lending-policy rulebook and compliance checks (agent 2).

The rulebook below is invented for this project. It belongs to the
fictional firm Tarnfield Community Credit Union and is cited by section
in every memo rationale, so a reader can trace each decision back to a
rule instead of trusting a narrative. Nothing here is a real lender's
policy, and no real policy text is reproduced.
"""

from credit_memo.models import PolicyResult

RULEBOOK_TITLE = "Tarnfield Community Credit Union - Synthetic Lending Policy v1.0"

# Each rule: id, rulebook section, title, severity, check, fail detail.
RULES = [
    {
        "rule_id": "POL-01",
        "section": "3.1",
        "title": "Maximum debt-to-income ratio",
        "severity": "hard",
        "check": lambda app: app.debt_to_income <= 0.43,
        "detail": "Debt-to-income ratio must not exceed 0.43.",
    },
    {
        "rule_id": "POL-02",
        "section": "3.2",
        "title": "Minimum credit score",
        "severity": "hard",
        "check": lambda app: app.credit_score >= 620,
        "detail": "Credit score must be at least 620.",
    },
    {
        "rule_id": "POL-03",
        "section": "3.3",
        "title": "Maximum loan-to-value ratio",
        "severity": "hard",
        "check": lambda app: app.loan_to_value <= 0.90,
        "detail": "Loan-to-value ratio must not exceed 0.90.",
    },
    {
        "rule_id": "POL-04",
        "section": "3.4",
        "title": "Recent delinquency limit",
        "severity": "hard",
        "check": lambda app: app.delinquencies_24m <= 1,
        "detail": "No more than one delinquency in the last 24 months.",
    },
    {
        "rule_id": "POL-05",
        "section": "3.5",
        "title": "Maximum loan amount",
        "severity": "hard",
        "check": lambda app: app.loan_amount <= 500_000,
        "detail": "Loan amount must not exceed 500,000 in synthetic currency units.",
    },
    {
        "rule_id": "POL-06",
        "section": "3.6",
        "title": "Stability or reserves compensating factor",
        "severity": "compensating",
        "check": lambda app: app.employment_years >= 1 or app.reserves_months >= 6,
        "detail": "At least one year of employment or six months of reserves required.",
    },
]


def check_policy(app) -> list:
    """Run every rulebook rule against one application."""
    results = []
    for rule in RULES:
        passed = bool(rule["check"](app))
        results.append(
            PolicyResult(
                rule_id=rule["rule_id"],
                section=rule["section"],
                title=rule["title"],
                severity=rule["severity"],
                passed=passed,
                detail=rule["detail"] + (" (met)" if passed else " (not met)"),
            )
        )
    return results


def hard_failures(results: list) -> list:
    return [r for r in results if not r.passed and r.severity == "hard"]


def compensating_failures(results: list) -> list:
    return [r for r in results if not r.passed and r.severity == "compensating"]
