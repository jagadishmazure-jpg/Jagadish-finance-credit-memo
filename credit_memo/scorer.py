"""Deterministic borrower risk scorer (agent 1).

The score is pure integer arithmetic: ``score = base + sum(contributions)``.
That identity is what makes the explainability layer exact rather than
approximate -- every memo shows per-feature contributions that sum to the
score, and a test proves the identity for every sample application.

This is a transparent rule-based scorer, not a trained model. It is a
teaching and demonstration artifact, not a lending decision engine.
"""

BASE_SCORE = 300

BANDS = (
    (750, "A - Low risk"),
    (650, "B - Moderate risk"),
    (550, "C - Elevated risk"),
    (0, "D - High risk"),
)


def _credit_score_points(app) -> int:
    s = app.credit_score
    if s >= 750:
        return 250
    if s >= 700:
        return 180
    if s >= 650:
        return 100
    if s >= 600:
        return 20
    return -120


def _dti_points(app) -> int:
    dti = app.debt_to_income
    if dti <= 0.28:
        return 150
    if dti <= 0.36:
        return 100
    if dti <= 0.43:
        return 30
    return -150


def _ltv_points(app) -> int:
    ltv = app.loan_to_value
    if ltv <= 0.70:
        return 100
    if ltv <= 0.80:
        return 60
    if ltv <= 0.90:
        return 0
    return -100


def _delinquency_points(app) -> int:
    if app.delinquencies_24m == 0:
        return 80
    if app.delinquencies_24m == 1:
        return -20
    return -120


def _employment_points(app) -> int:
    if app.employment_years >= 5:
        return 60
    if app.employment_years >= 2:
        return 30
    return -20


def _reserves_points(app) -> int:
    if app.reserves_months >= 6:
        return 60
    if app.reserves_months >= 3:
        return 30
    return 0


FEATURES = (
    ("credit_score", _credit_score_points),
    ("debt_to_income", _dti_points),
    ("loan_to_value", _ltv_points),
    ("delinquencies_24m", _delinquency_points),
    ("employment_years", _employment_points),
    ("reserves_months", _reserves_points),
)


def band_for_score(score: int) -> str:
    for threshold, band in BANDS:
        if score >= threshold:
            return band
    raise AssertionError("unreachable: lowest band threshold is 0")


def score_application(app) -> "RiskResult":
    from credit_memo.models import RiskResult

    contributions = {name: fn(app) for name, fn in FEATURES}
    score = BASE_SCORE + sum(contributions.values())
    return RiskResult(
        score=score,
        band=band_for_score(score),
        base_score=BASE_SCORE,
        contributions=contributions,
    )
