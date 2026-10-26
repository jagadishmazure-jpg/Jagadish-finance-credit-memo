"""Email channel. Dry-run by default, always.

There is no SMTP backend in this repo and no credential is ever read,
stored, or accepted here. ``send`` in dry-run mode returns a record of
what WOULD have been sent and transmits nothing. Real sending requires
an explicit opt-in AND a non-CI environment; in CI the call is refused
outright, so a test run can never leak a memo.
"""

import os


class EmailRefused(Exception):
    pass


class EmailChannel:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.sent = []

    def send(self, to, subject, body, opt_in=False):
        if os.environ.get("CI") == "true":
            raise EmailRefused("email sending is refused in CI")
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
