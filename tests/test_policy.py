"""Policy rulebook tests: every rule has an id, a section, and a
pass/fail case; hard and compensating failures are distinguished."""

from credit_memo.models import Application
from credit_memo.policy import (
    RULES,
    check_policy,
    compensating_failures,
    hard_failures,
)


def _base(**over):
    kw = dict(
        app_ref="APP-TEST",
        annual_income=100000,
        monthly_debt=2000,
        loan_amount=200000,
        property_value=300000,
        credit_score=720,
        delinquencies_24m=0,
        employment_years=4,
        reserves_months=4,
    )
    kw.update(over)
    return Application(**kw)


def test_every_rule_has_id_section_and_severity():
    for rule in RULES:
        assert rule["rule_id"].startswith("POL-")
        assert rule["section"]
        assert rule["severity"] in ("hard", "compensating")


def test_rule_ids_are_unique():
    ids = [r["rule_id"] for r in RULES]
    assert len(ids) == len(set(ids))


def test_clean_application_passes_all_rules():
    results = check_policy(_base())
    assert all(r.passed for r in results)


def test_dti_rule_fails():
    results = {r.rule_id: r for r in check_policy(_base(monthly_debt=5000))}
    assert not results["POL-01"].passed
    assert results["POL-01"].section == "3.1"


def test_credit_score_rule_fails():
    results = {r.rule_id: r for r in check_policy(_base(credit_score=600))}
    assert not results["POL-02"].passed


def test_ltv_rule_fails():
    results = {r.rule_id: r for r in check_policy(_base(loan_amount=290000))}
    assert not results["POL-03"].passed


def test_delinquency_rule_fails():
    results = {r.rule_id: r for r in check_policy(_base(delinquencies_24m=2))}
    assert not results["POL-04"].passed


def test_loan_amount_rule_fails():
    results = {r.rule_id: r for r in check_policy(_base(loan_amount=600000))}
    assert not results["POL-05"].passed


def test_compensating_rule_fails_but_is_not_hard():
    app = _base(employment_years=0.5, reserves_months=2)
    results = check_policy(app)
    comp = compensating_failures(results)
    assert [r.rule_id for r in comp] == ["POL-06"]
    assert hard_failures(results) == []


def test_hard_failures_helper():
    results = check_policy(_base(monthly_debt=5000, credit_score=600))
    assert {r.rule_id for r in hard_failures(results)} == {"POL-01", "POL-02"}
