"""KYC tests: pass path and every failure mode."""

from credit_memo.kyc import validate_kyc
from credit_memo.models import KycEvidence


def _evidence(**over):
    kw = dict(
        government_id_present=True,
        name_matches_application=True,
        address_verified=True,
        sanctions_screen_clear=True,
    )
    kw.update(over)
    return KycEvidence(**kw)


def test_clean_kyc_passes():
    result = validate_kyc(_evidence())
    assert result.status == "PASS"
    assert result.blockers == []


def test_missing_id_fails():
    result = validate_kyc(_evidence(government_id_present=False))
    assert result.status == "FAIL"
    assert "government_id_present" in result.blockers


def test_name_mismatch_fails():
    result = validate_kyc(_evidence(name_matches_application=False))
    assert "name_matches_application" in result.blockers


def test_unverified_address_fails():
    result = validate_kyc(_evidence(address_verified=False))
    assert "address_verified" in result.blockers


def test_sanctions_hit_is_a_hard_blocker():
    result = validate_kyc(_evidence(sanctions_screen_clear=False))
    assert result.status == "FAIL"
    assert "sanctions_screen_clear" in result.blockers


def test_every_check_reports_a_detail():
    result = validate_kyc(_evidence())
    assert len(result.checks) == 4
    assert all(c.detail for c in result.checks)
