"""PII redaction tests. The checklist covers card numbers and email
addresses in addition to phone numbers and SSNs. Probe values below
are synthetic test fixtures, not real people's data.
"""

from credit_memo.kyc import validate_kyc
from credit_memo.memo import build_memo
from credit_memo.models import Application, KycEvidence
from credit_memo.policy import check_policy
from credit_memo.redaction import contains_pii, redact_text
from credit_memo.scorer import score_application

PROBE = {
    "ssn": "123-45-6789",
    "phone": "(555) 123-4567",
    "email": "borrower@example.invalid",
    "card_spaced": "4111 1111 1111 1111",
    "card_dashed": "4111-1111-1111-1111",
    "card_plain": "4111111111111111",
}


def test_ssn_redacted():
    assert PROBE["ssn"] not in redact_text(f"ssn {PROBE['ssn']}")
    assert "[REDACTED-SSN]" in redact_text(PROBE["ssn"])


def test_phone_redacted():
    assert "[REDACTED-PHONE]" in redact_text(f"call {PROBE['phone']}")


def test_email_redacted():
    out = redact_text(f"contact {PROBE['email']}")
    assert PROBE["email"] not in out
    assert "[REDACTED-EMAIL]" in out


def test_card_numbers_redacted_all_formats():
    for key in ("card_spaced", "card_dashed", "card_plain"):
        out = redact_text(f"card {PROBE[key]}")
        assert PROBE[key] not in out
        assert "[REDACTED-CARD]" in out


def test_contains_pii_detects_each_type():
    for value in PROBE.values():
        assert contains_pii(value)


def test_clean_text_untouched():
    text = "Application APP-2026-001 scored 960 in band A."
    assert redact_text(text) == text
    assert not contains_pii(text)


def test_memo_never_contains_borrower_pii():
    app = Application(
        app_ref="APP-2026-099",
        annual_income=120000, monthly_debt=2000, loan_amount=240000,
        property_value=320000, credit_score=760, delinquencies_24m=0,
        employment_years=6, reserves_months=8,
        borrower_name="Synthetic Probe Person",
        borrower_email=PROBE["email"],
        borrower_ssn=PROBE["ssn"],
        borrower_phone=PROBE["phone"],
        borrower_card=PROBE["card_spaced"],
    )
    kyc = validate_kyc(
        KycEvidence(True, True, True, True)
    )
    memo = build_memo(app, score_application(app), check_policy(app), kyc, "MEMO-TEST")
    for value in (
        "Synthetic Probe Person",
        PROBE["email"],
        PROBE["ssn"],
        PROBE["phone"],
        PROBE["card_spaced"],
    ):
        assert value not in memo.text
    assert not contains_pii(memo.text)


def test_log_lines_are_redacted_before_writing():
    raw_log = (
        f"memo failed for {PROBE['email']} card {PROBE['card_plain']} "
        f"phone {PROBE['phone']}"
    )
    clean = redact_text(raw_log)
    assert not contains_pii(clean)
    assert PROBE["email"] not in clean


def test_redaction_is_idempotent():
    once = redact_text(f"email {PROBE['email']} ssn {PROBE['ssn']}")
    assert redact_text(once) == once
