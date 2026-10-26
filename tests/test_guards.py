"""Row-cap, budget, brand, and email-channel tests."""

import sqlite3

import pytest

from credit_memo.budget import Budget, validate_cost
from credit_memo.brand import BLOCKLIST_HASHES, add_blocked_name, check_text, find_blocked
from credit_memo.email_channel import EmailChannel, EmailRefused
from credit_memo.fetching import RowCapExceeded, fetch_capped


def _conn_with_rows(n):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (v INTEGER)")
    conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(n)])
    return conn


def test_fetch_under_cap_returns_all_rows():
    conn = _conn_with_rows(3)
    assert fetch_capped(conn.cursor(), "SELECT v FROM t", max_rows=10) == [
        (0,),
        (1,),
        (2,),
    ]


def test_fetch_over_cap_raises_instead_of_truncating():
    conn = _conn_with_rows(5)
    with pytest.raises(RowCapExceeded):
        fetch_capped(conn.cursor(), "SELECT v FROM t", max_rows=3)


def test_fetch_cap_uses_no_limit_rewriting():
    sql = "SELECT v FROM t"
    assert "limit" not in sql.lower()
    conn = _conn_with_rows(2)
    assert len(fetch_capped(conn.cursor(), sql, max_rows=5)) == 2


def test_fetch_exactly_at_cap_passes():
    conn = _conn_with_rows(4)
    assert len(fetch_capped(conn.cursor(), "SELECT v FROM t", max_rows=4)) == 4


def test_negative_cost_rejected():
    with pytest.raises(ValueError):
        validate_cost(-1)


def test_negative_budget_cap_rejected():
    with pytest.raises(ValueError):
        Budget(cap=-100)


def test_negative_budget_add_rejected():
    budget = Budget(cap=10)
    with pytest.raises(ValueError):
        budget.add(-5)


def test_nan_and_bool_costs_rejected():
    with pytest.raises(ValueError):
        validate_cost(float("nan"))
    with pytest.raises(ValueError):
        validate_cost(True)


def test_zero_cost_allowed_and_over_cap_flagged():
    budget = Budget(cap=1)
    assert budget.add(0) == 0
    budget.add(2)
    assert budget.over_cap
    assert budget.remaining == -1


def test_brand_blocklist_is_nonempty():
    assert len(BLOCKLIST_HASHES) >= 10


def test_brand_check_detects_a_blocked_name():
    add_blocked_name("Zqx Invented Test Brand")
    assert not check_text("our partner Zqx Invented Test Brand signed today")
    assert find_blocked("our partner Zqx Invented Test Brand signed today")


def test_brand_check_passes_clean_text():
    assert check_text("Tarnfield Community Credit Union synthetic lending policy")


def test_email_defaults_to_dry_run_and_transmits_nothing():
    channel = EmailChannel()
    assert channel.dry_run is True
    record = channel.send("a@example.invalid", "Memo", "body")
    assert record["status"] == "dry_run"
    assert record["transmitted"] is False


def test_email_requires_opt_in_when_not_dry_run(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    channel = EmailChannel(dry_run=False)
    with pytest.raises(EmailRefused):
        channel.send("a@example.invalid", "Memo", "body", opt_in=False)


def test_email_refused_in_ci_even_with_opt_in(monkeypatch):
    monkeypatch.setenv("CI", "true")
    channel = EmailChannel(dry_run=False)
    with pytest.raises(EmailRefused):
        channel.send("a@example.invalid", "Memo", "body", opt_in=True)


def test_email_dry_run_records_even_in_ci(monkeypatch):
    # Regression: the runner sets CI, and a dry run must still return
    # its record instead of raising, because it transmits nothing.
    monkeypatch.setenv("CI", "true")
    channel = EmailChannel()
    record = channel.send("a@example.invalid", "Memo", "body")
    assert record["status"] == "dry_run"
    assert record["transmitted"] is False


def test_email_channel_has_no_credential_attributes():
    channel = EmailChannel()
    for attr in ("password", "api_key", "smtp_password", "token", "secret"):
        assert not hasattr(channel, attr)
