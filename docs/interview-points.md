# Interview points

## The one-minute version

"I built a six-agent credit memo pipeline over synthetic data. A
deterministic scorer bands the borrower, policy checks cite a
synthetic rulebook by section, KYC gates the deal, and the memo shows
per-feature contributions that sum exactly to the score — so a
reviewer can see why, not just what. Nothing becomes final without a
named-person, single-use, expiring approval, and the database only
answers through views."

## Points to land, with evidence

- **Explainability that is exact, not plausible.** The scorer uses
  integer arithmetic and no clamping, so contributions sum to the
  score by construction — and a test proves it for every sample.
  Ask: what breaks if you clamp the score? The sum identity.
- **Policy overrides score.** A band-A application with a loan above
  the synthetic cap is declined (sample APP-2026-005). The system
  refuses to let a good score launder a policy breach.
- **Gates are tested at their failure modes, not just the happy
  path.** Bypass, reject, absent, low-confidence, and
  self-contradicting consent each have their own test. A gate that
  only passes its happy path is decoration.
- **The authorizer is view-aware, not table-aware.** A base-table
  read is allowed only when it flows through an allowed view; direct
  reads, `sqlite_master`, writes, PRAGMA, and ATTACH are denied at
  runtime. The test file says plainly that its text check is
  disabled, because denial tests must contain probe strings.
- **PII redaction includes cards and emails.** Most checklists stop
  at phone and SSN; this one redacts card numbers in three formats
  and email addresses, in memos, logs, and errors.
- **Honest numbers.** 90 tests over 5 synthetic fixtures. That is a
  regression claim, not an accuracy claim — and the limitations doc
  says so.

## Questions to expect

- *Why a rule-table scorer instead of a model?* Transparency first:
  exact explanations and a testable invariant beat a black box in a
  regulated workflow. A model would need calibration, monitoring, and
  a fairness audit this scaffold does not claim.
- *What would you change for production?* A persistent writer
  service, a real KYC provider, a fairness audit, and a language
  model used only for narration over the cited facts — never as the
  decision-maker.
- *Why deny writes in the store instead of just not issuing them?*
  Defence in depth: the layer that answers queries should not be
  able to change data even if a caller is confused or compromised.
