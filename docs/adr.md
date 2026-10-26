# Architecture Decision Records

## ADR-1: Deterministic rule-table scorer, not a trained model

- **Context.** The memo must explain itself exactly.
- **Decision.** Integer point tables per feature; score = base +
  sum of contributions; no clamping, no rounding.
- **Consequences.** Explanations are exact and testable. The scorer
  cannot learn and its bands are uncalibrated — recorded as a
  limitation, not hidden.

## ADR-2: View-aware authorizer, not application-level filtering

- **Context.** PII lives in base tables; readers must never see it.
- **Decision.** Enforce at the SQLite authorizer: base-table reads
  allowed only through allowed views; everything else denied.
- **Consequences.** A buggy or malicious query fails at the database
  layer instead of relying on every caller to filter. The store is
  read-only after seeding until a separate writer service exists.

## ADR-3: Approval as a named-person, single-use, scoped, expiring token

- **Context.** "Someone approved it" is not auditable.
- **Decision.** Tokens name one person, cover one memo, work once,
  and expire. Consent must be unambiguous and high-confidence.
- **Consequences.** Every failure mode (wrong person, reuse, wrong
  memo, expiry, weak or contradictory consent) is a distinct error
  with its own test.

## ADR-4: Redact at the boundary, and never read PII in synthesis

- **Context.** A redaction-only defence fails the day someone forgets
  to redact.
- **Decision.** Two layers: the memo builder never references PII
  fields, and the finished text is redaction-swept anyway.
- **Consequences.** A leak would require both layers to fail. The
  PII checklist includes card numbers and email addresses, not just
  phone and SSN.

## ADR-5: Row cap with fetchmany, never LIMIT rewriting

- **Context.** Silent truncation hides data loss; query rewriting
  hides intent.
- **Decision.** `fetchmany(MAX+1)`; overflow raises.
- **Consequences.** Callers see the failure and choose a narrower
  query. Queries stay exactly as written.

## ADR-6: Synthetic data only, fictional firm only

- **Context.** The source case material involves real loan data.
- **Decision.** This repo invents its firm, its rulebook, and every
  application. No real data, no real firm names, no affiliation
  claims.
- **Consequences.** The repo is safe to publish and to demo, and its
  numbers are honestly labelled as regression fixtures.
