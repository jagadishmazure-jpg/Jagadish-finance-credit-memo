"""Scorer tests: determinism, exact contribution identity, band edges."""

import pytest

from credit_memo.models import Application
from credit_memo.samples import SAMPLES
from credit_memo.scorer import BASE_SCORE, band_for_score, score_application


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


def test_score_is_deterministic():
    app = _base()
    assert score_application(app) == score_application(app)


def test_contributions_sum_to_score_minus_base_for_all_samples():
    for app in SAMPLES:
        result = score_application(app)
        assert result.base_score + sum(result.contributions.values()) == result.score


def test_contributions_cover_all_six_features():
    result = score_application(_base())
    assert set(result.contributions) == {
        "credit_score",
        "debt_to_income",
        "loan_to_value",
        "delinquencies_24m",
        "employment_years",
        "reserves_months",
    }


@pytest.mark.parametrize(
    "score,band",
    [
        (900, "A - Low risk"),
        (750, "A - Low risk"),
        (749, "B - Moderate risk"),
        (650, "B - Moderate risk"),
        (649, "C - Elevated risk"),
        (550, "C - Elevated risk"),
        (549, "D - High risk"),
    ],
)
def test_band_boundaries(score, band):
    assert band_for_score(score) == band


def test_higher_credit_score_scores_higher():
    low = score_application(_base(credit_score=610))
    high = score_application(_base(credit_score=780))
    assert high.score > low.score
    assert high.contributions["credit_score"] > low.contributions["credit_score"]


def test_high_dti_penalised():
    ok = score_application(_base(monthly_debt=2000))
    bad = score_application(_base(monthly_debt=5000))
    assert bad.contributions["debt_to_income"] < ok.contributions["debt_to_income"]


def test_zero_income_raises_without_pii():
    app = _base(annual_income=0, borrower_email="probe@example.invalid")
    with pytest.raises(ValueError) as excinfo:
        _ = app.debt_to_income
    assert "probe@example.invalid" not in str(excinfo.value)


def test_zero_property_value_raises():
    app = _base(property_value=0)
    with pytest.raises(ValueError):
        _ = app.loan_to_value
