"""View-aware SQLite store.

The authorizer is the enforcement point, and it is strict:

- A read of a BASE table is allowed only when the authorizer's
  trigger/view argument names an allowed view (i.e. the read flows
  through that view). A direct read of a base table has an empty source
  argument and is denied.
- A read of an allowed view itself is allowed (it is the public surface).
- Any other table -- including sqlite_master -- is denied.
- Every write (INSERT, UPDATE, DELETE), every PRAGMA, ATTACH, DETACH,
  ALTER, DROP, CREATE, and every other action is denied.
- Loading extensions is refused by construction: the connection class
  raises on enable_load_extension, and this codebase never enables it.

Schema is created BEFORE the authorizer is installed, so seeding is
possible; after installation the connection is read-only through views.
"""

import sqlite3

BASE_TABLES = {"applications", "memos"}
ALLOWED_VIEWS = {"v_application_metrics", "v_memo_status"}

_SAFE_FUNCTIONS = {
    "count",
    "sum",
    "avg",
    "min",
    "max",
    "coalesce",
    "length",
    "lower",
    "upper",
    "abs",
    "round",
}

_SCHEMA = """
CREATE TABLE applications (
    app_ref TEXT PRIMARY KEY,
    annual_income REAL,
    monthly_debt REAL,
    loan_amount REAL,
    property_value REAL,
    credit_score INTEGER,
    delinquencies_24m INTEGER,
    employment_years REAL,
    reserves_months REAL,
    borrower_name TEXT,
    borrower_email TEXT,
    borrower_ssn TEXT,
    borrower_phone TEXT,
    borrower_card TEXT
);
CREATE TABLE memos (
    memo_id TEXT PRIMARY KEY,
    app_ref TEXT,
    status TEXT,
    recommendation TEXT
);
CREATE VIEW v_application_metrics AS
    SELECT app_ref, annual_income, monthly_debt, loan_amount,
           property_value, credit_score, delinquencies_24m,
           employment_years, reserves_months
    FROM applications;
CREATE VIEW v_memo_status AS
    SELECT memo_id, app_ref, status, recommendation FROM memos;
"""

# Synthetic seed rows. PII columns use the .invalid domain and invented
# values so they can never be mistaken for real people; views hide them.
_SEED_APPLICATIONS = [
    ("APP-2026-001", 120000, 2000, 240000, 320000, 760, 0, 6, 8,
     "Synthetic Person A", "synthetic-a@example.invalid", "111-22-3333",
     "(555) 010-1001", "4111 1111 1111 1111"),
    ("APP-2026-002", 80000, 2600, 300000, 340000, 640, 1, 2, 2,
     "Synthetic Person B", "synthetic-b@example.invalid", "222-33-4444",
     "(555) 010-1002", "5500 0055 5555 5559"),
]


def _authorizer(action, arg1, arg2, db_name, source):
    """SQLite authorizer callback. Return SQLITE_OK or SQLITE_DENY."""
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_TRANSACTION:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        if arg1 in BASE_TABLES:
            # Base-table columns may only be read through an allowed view.
            if source in ALLOWED_VIEWS:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY
        if arg1 in ALLOWED_VIEWS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION:
        name = (arg2 or arg1 or "").lower()
        if name in _SAFE_FUNCTIONS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    # Everything else -- writes, PRAGMA, ATTACH, DETACH, ALTER, DROP,
    # CREATE, ANALYZE, SAVEPOINT, REINDEX -- is denied.
    return sqlite3.SQLITE_DENY


class RestrictedConnection(sqlite3.Connection):
    """A connection that refuses extension loading outright."""

    def enable_load_extension(self, enabled):  # noqa: D102 - intentional guard
        raise PermissionError("extension loading is refused by this store")


def open_store(path=":memory:"):
    """Create a seeded store, then install the strict authorizer."""
    conn = sqlite3.connect(path, factory=RestrictedConnection)
    conn.executescript(_SCHEMA)
    conn.executemany(
        "INSERT INTO applications VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        _SEED_APPLICATIONS,
    )
    conn.execute(
        "INSERT INTO memos VALUES (?,?,?,?)",
        ("MEMO-2026-001", "APP-2026-001", "DRAFT", "Approve"),
    )
    conn.commit()
    conn.set_authorizer(_authorizer)
    return conn
