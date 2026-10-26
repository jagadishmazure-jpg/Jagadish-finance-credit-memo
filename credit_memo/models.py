"""Data models. All borrower fields are synthetic; PII fields exist only so
the redaction and view layers have something to prove they hide.

A memo never carries PII fields: the synthesis layer only reads the
numeric/financial fields and the application reference.
"""

from dataclasses import dataclass, field


@dataclass
class Application:
    """One synthetic loan application."""

    app_ref: str
    annual_income: float
    monthly_debt: float
    loan_amount: float
    property_value: float
    credit_score: int
    delinquencies_24m: int
    employment_years: float
    reserves_months: float
    # Optional synthetic PII probes. Never copied into memos, logs, or errors.
    borrower_name: str | None = None
    borrower_email: str | None = None
    borrower_ssn: str | None = None
    borrower_phone: str | None = None
    borrower_card: str | None = None

    @property
    def debt_to_income(self) -> float:
        if self.annual_income <= 0:
            raise ValueError("annual_income must be positive to compute DTI")
        return (self.monthly_debt * 12.0) / self.annual_income

    @property
    def loan_to_value(self) -> float:
        if self.property_value <= 0:
            raise ValueError("property_value must be positive to compute LTV")
        return self.loan_amount / self.property_value


@dataclass
class RiskResult:
    score: int
    band: str
    base_score: int
    contributions: dict


@dataclass
class PolicyResult:
    rule_id: str
    section: str
    title: str
    severity: str
    passed: bool
    detail: str


@dataclass
class KycCheck:
    name: str
    passed: bool
    detail: str


@dataclass
class KycResult:
    status: str  # "PASS" or "FAIL"
    checks: list
    blockers: list


@dataclass
class KycEvidence:
    government_id_present: bool
    name_matches_application: bool
    address_verified: bool
    sanctions_screen_clear: bool


@dataclass
class Memo:
    memo_id: str
    app_ref: str
    status: str  # "DRAFT" or "FINAL"
    recommendation: str
    risk_band: str
    score: int
    contributions: dict
    policy_results: list
    kyc_status: str
    conditions: list
    rationale: list
    text: str = ""
    approved_by: str | None = None
    approval_token: str | None = None
