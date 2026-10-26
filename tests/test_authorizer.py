"""Authorizer tests -- RUNTIME proofs, text check disabled.

Read this before "fixing" anything here: these tests intentionally
contain probe strings (sqlite_master, DROP, ATTACH, INSERT, PRAGMA)
because that is what a denial test must attempt. Any naive source-text
scan that flags forbidden keywords MUST exempt this file; the proof of
enforcement is the sqlite3.DatabaseError (or PermissionError) raised
at runtime below, never the presence or absence of a string in source.

The authorizer rule under test: a base-table read is allowed only when
the authorizer's source argument names an allowed view; direct reads,
sqlite_master, all writes, PRAGMA, ATTACH, and extension loading are
denied.
"""

import sqlite3

import pytest

from credit_memo.store import ALLOWED_VIEWS, open_store


def test_view_read_allowed():
    conn = open_store()
    rows = conn.execute("SELECT app_ref FROM v_application_metrics").fetchall()
    assert [r[0] for r in rows] == ["APP-2026-001", "APP-2026-002"]


def test_memo_status_view_read_allowed():
    conn = open_store()
    rows = conn.execute("SELECT memo_id, status FROM v_memo_status").fetchall()
    assert rows == [("MEMO-2026-001", "DRAFT")]


def test_direct_base_table_read_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT app_ref FROM applications").fetchall()


def test_direct_memos_table_read_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT memo_id FROM memos").fetchall()


def test_sqlite_master_read_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT name FROM sqlite_master").fetchall()


def test_insert_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("INSERT INTO memos VALUES ('M2', 'APP-2026-001', 'DRAFT', 'Approve')")


def test_update_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("UPDATE memos SET status='FINAL' WHERE memo_id='MEMO-2026-001'")


def test_delete_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DELETE FROM memos WHERE memo_id='MEMO-2026-001'")


def test_pragma_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("PRAGMA foreign_keys=ON").fetchall()


def test_attach_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("ATTACH ':memory:' AS other")


def test_drop_denied():
    conn = open_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DROP TABLE memos")


def test_load_extension_refused():
    conn = open_store()
    with pytest.raises(PermissionError):
        conn.enable_load_extension(True)


def test_view_cursor_exposes_no_pii_columns():
    conn = open_store()
    cursor = conn.execute("SELECT * FROM v_application_metrics")
    names = [d[0] for d in cursor.description]
    assert not any(n.startswith("borrower_") for n in names)
    assert set(names) == {
        "app_ref",
        "annual_income",
        "monthly_debt",
        "loan_amount",
        "property_value",
        "credit_score",
        "delinquencies_24m",
        "employment_years",
        "reserves_months",
    }


def test_allowed_views_are_nonempty():
    assert ALLOWED_VIEWS == {"v_application_metrics", "v_memo_status"}
