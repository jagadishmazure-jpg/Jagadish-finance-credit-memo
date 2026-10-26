# Security Policy

## Scope

This is a demonstration project using synthetic data only. It makes no
lending decisions, holds no real borrower data, and has no production
deployment. Treat it as sample code: review the guardrails in
`docs/guardrails.md` before adapting any of it.

## Reporting a vulnerability

If you find a security issue in this sample code, open an issue
describing the flaw and a minimal reproduction. Do not include real
personal data in any report.

## What is already guarded

- SQLite access is restricted by a strict authorizer (views only, no
  writes, no PRAGMA, no ATTACH, no extension loading).
- Memos, logs, and errors are swept for PII, including card numbers
  and email addresses.
- Memo finalisation requires a named-person, single-use, scoped,
  expiring approval.
- Email is dry-run by default and refused in CI.
- No credentials, tokens, or secrets are stored in this repo.
