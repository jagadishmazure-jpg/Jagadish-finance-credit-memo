# Limitations and known failures

These are kept visible on purpose. A limitation that is hidden is a
limitation that will surprise someone later.

- **Rule-table scorer, not a model.** Bands and point values are
  invented for demonstration. They are not calibrated on any data,
  and nothing here should be used to judge a real borrower.
- **Template memos, not language-model prose.** Synthesis is
  deterministic text assembly. Memos are consistent and auditable,
  but formulaic; a language-model narration layer is planned, not
  built.
- **Read-only store.** After seeding, the SQLite connection denies
  all writes, so finalised memos are not persisted. A writer service
  with its own authorisation is planned work, not a hidden feature.
- **Boolean KYC.** Evidence is four flags, not document checks,
  biometrics, or sanctions-list matching against a real list.
- **Five synthetic samples.** The suite is 90 regression checks over
  synthetic fixtures. That proves the code behaves as specified; it
  proves nothing about real-world accuracy, fairness, or coverage.
- **No fairness audit.** The scorer's features and thresholds have
  not been tested for disparate impact. Any real use would need that
  analysis before anything else.
- **No concurrency story.** The approval gate is in-memory. Two
  processes would not share token state.
- **Cost units are illustrative.** Budget figures are synthetic
  units for demonstrating the guard, not prices from any provider.

## Known failure modes, as tests

- An approval token redeemed twice fails (`ApprovalAlreadyUsed`).
- A memo finalised without approval fails (`ApprovalRequired`).
- A query over the row cap fails (`RowCapExceeded`) instead of
  silently truncating.
- A negative cost fails (`ValueError`) instead of inflating budget.
- A direct base-table read fails (`sqlite3.DatabaseError`) instead
  of returning PII.
