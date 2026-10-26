"""Synthetic sample applications. No real people, no real data.

Five profiles spanning the decision space: a clean approval, a
borderline referral, a high-debt decline, a thin-file referral, and a
policy-breaching decline. Tests and the demo run against these five;
they are regression fixtures, not evidence about real borrowers.
"""

from credit_memo.models import Application, KycEvidence

SAMPLES = [
    Application(
        app_ref="APP-2026-001",
        annual_income=120000, monthly_debt=2000, loan_amount=240000,
        property_value=320000, credit_score=760, delinquencies_24m=0,
        employment_years=6, reserves_months=8,
    ),
    Application(
        app_ref="APP-2026-002",
        annual_income=95000, monthly_debt=2800, loan_amount=280000,
        property_value=350000, credit_score=690, delinquencies_24m=0,
        employment_years=4, reserves_months=4,
    ),
    Application(
        app_ref="APP-2026-003",
        annual_income=60000, monthly_debt=2800, loan_amount=200000,
        property_value=230000, credit_score=640, delinquencies_24m=1,
        employment_years=3, reserves_months=1,
    ),
    Application(
        app_ref="APP-2026-004",
        annual_income=75000, monthly_debt=1500, loan_amount=180000,
        property_value=260000, credit_score=700, delinquencies_24m=0,
        employment_years=0.5, reserves_months=2,
    ),
    Application(
        app_ref="APP-2026-005",
        annual_income=90000, monthly_debt=2200, loan_amount=520000,
        property_value=600000, credit_score=710, delinquencies_24m=0,
        employment_years=5, reserves_months=6,
    ),
]

CLEAN_KYC = KycEvidence(
    government_id_present=True,
    name_matches_application=True,
    address_verified=True,
    sanctions_screen_clear=True,
)

FAILED_KYC = KycEvidence(
    government_id_present=True,
    name_matches_application=False,
    address_verified=False,
    sanctions_screen_clear=False,
)
