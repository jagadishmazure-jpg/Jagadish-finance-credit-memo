# Guardrails and security controls

Every control below names the test that proves it. If the README says
something is enforced, a test must show it — and here is where to
look.

## SQLite authorizer (`credit_memo/store.py`)

| Claim | Proof test |
| --- | --- |
| View reads allowed | `test_view_read_allowed`, `test_memo_status_view_read_allowed` |
| Direct base-table reads denied | `test_direct_base_table_read_denied`, `test_direct_memos_table_read_denied` |
| `sqlite_master` denied | `test_sqlite_master_read_denied` |
| INSERT / UPDATE / DELETE denied | `test_insert_denied`, `test_update_denied`, `test_delete_denied` |
| PRAGMA denied | `test_pragma_denied` |
| ATTACH denied | `test_attach_denied` |
| DROP denied | `test_drop_denied` |
| Extension loading refused | `test_load_extension_refused` |
| Views expose no PII columns | `test_view_cursor_exposes_no_pii_columns` |

Authorizer tests run with the text check disabled: the test file
intentionally contains probe strings, and its header says so. The
proof is the runtime error, not a string scan.

## Approval gate (`credit_memo/approval.py`)

| Claim | Proof test |
| --- | --- |
| Bypass (no approval) rejected | `test_bypass_finalize_without_approval_raises` |
| Explicit refusal rejected | `test_reject_explicit_no_raises` |
| Absent approval rejected | `test_absent_unknown_token_raises` |
| Low-confidence "yes" rejected | `test_low_confidence_yes_raises` |
| Self-contradicting consent rejected | `test_self_contradicting_consent_raises`, `test_yes_wait_without_no_is_still_not_clean_consent` |
| Single-use enforced | `test_single_use_token_cannot_be_reused` |
| Named-person enforced | `test_wrong_person_cannot_approve` |
| Expiry enforced | `test_expired_token_raises` |
| Scope enforced | `test_decision_scoped_to_one_memo` |
| Threshold boundary 0.7 | `test_confidence_threshold_boundary` |

## PII redaction (`credit_memo/redaction.py`)

Card numbers (spaced, dashed, plain) and email addresses are redacted
alongside SSNs and phone numbers. Proof: `test_ssn_redacted`,
`test_phone_redacted`, `test_email_redacted`,
`test_card_numbers_redacted_all_formats`,
`test_memo_never_contains_borrower_pii` (a memo built from an
application carrying every PII field contains none of them),
`test_log_lines_are_redacted_before_writing`.

## Row cap, budget, brand, email

| Claim | Proof test |
| --- | --- |
| Row cap via `fetchmany(MAX+1)`, no LIMIT rewriting, overflow raises | `test_fetch_over_cap_raises_instead_of_truncating`, `test_fetch_cap_uses_no_limit_rewriting`, `test_fetch_exactly_at_cap_passes` |
| Negative / NaN / boolean costs rejected | `test_negative_cost_rejected`, `test_negative_budget_cap_rejected`, `test_negative_budget_add_rejected`, `test_nan_and_bool_costs_rejected` |
| Brand blocklist non-empty; detection works; docs clean | `test_brand_blocklist_is_nonempty`, `test_brand_check_detects_a_blocked_name`, `test_repo_docs_contain_no_blocked_names` |
| Email dry-run by default, opt-in required, refused in CI, no credentials | `test_email_defaults_to_dry_run_and_transmits_nothing`, `test_email_requires_opt_in_when_not_dry_run`, `test_email_refused_in_ci_even_with_opt_in`, `test_email_channel_has_no_credential_attributes` |

## Explainability

| Claim | Proof test |
| --- | --- |
| Contributions sum to score minus base, for all samples | `test_contributions_sum_to_score_minus_base_for_all_samples` |
| Memo carries the same contributions as the scorer | `test_memo_contributions_sum_line_is_exact` |
