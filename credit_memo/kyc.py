"""KYC validation step (agent 3).

Synthetic checks only: document presence, name match, address
verification, and a sanctions-screen flag. A failed sanctions screen is a
hard blocker. No real identity data is involved; evidence objects carry
booleans, never documents or personal details.
"""

from credit_memo.models import KycCheck, KycResult


def validate_kyc(evidence) -> KycResult:
    checks = [
        KycCheck(
            "government_id_present",
            bool(evidence.government_id_present),
            "Government-issued ID on file." if evidence.government_id_present
            else "No government-issued ID on file.",
        ),
        KycCheck(
            "name_matches_application",
            bool(evidence.name_matches_application),
            "ID name matches the application." if evidence.name_matches_application
            else "ID name does not match the application.",
        ),
        KycCheck(
            "address_verified",
            bool(evidence.address_verified),
            "Address verified." if evidence.address_verified
            else "Address not verified.",
        ),
        KycCheck(
            "sanctions_screen_clear",
            bool(evidence.sanctions_screen_clear),
            "Sanctions screen clear." if evidence.sanctions_screen_clear
            else "Sanctions screen hit: hard blocker.",
        ),
    ]
    blockers = [c.name for c in checks if not c.passed]
    return KycResult(
        status="PASS" if not blockers else "FAIL",
        checks=checks,
        blockers=blockers,
    )
