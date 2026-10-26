"""Email channel. Dry-run by default, always.

There is no SMTP backend in this repo and no credential is ever read,
stored, or accepted here. ``send`` in dry-run mode returns a record of
what WOULD have been sent and transmits nothing. Real sending requires
an explicit opt-in AND a non-CI environment; in CI a real send is refused
outright, so a test run can never leak a memo. A dry-run record is still
returned in CI, because it transmits nothing.
"""

import os


class EmailRefused(Exception):
    pass


class EmailChannel:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.sent = []

    def send(self, to, subject, body, opt_in=False):
        # Dry-run first: a dry run transmits nothing, so it must never
        # raise, even when the runner sets CI. The CI refusal below only
        # guards real sends, which is what it was meant to guard.
        if self.dry_run:
            record = {
                "to": to,
                "subject": subject,
                "body": body,
                "status": "dry_run",
                "transmitted": False,
            }
            self.sent.append(record)
            return record
        if os.environ.get("CI") == "true":
            raise EmailRefused("email sending is refused in CI")
        if not opt_in:
            raise EmailRefused("explicit opt-in is required to send email")
        # No transport exists in this repo: even opted-in sends are only
        # queued as records. Nothing is transmitted by this code.
        record = {
            "to": to,
            "subject": subject,
            "body": body,
            "status": "queued_no_transport",
            "transmitted": False,
        }
        self.sent.append(record)
        return record
