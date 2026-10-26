# Related repos

This repo is one finance build among several; each covers a distinct
slice so work is cross-linked rather than duplicated.

- **Finance KYC/AML pipeline (planned companion).** Deepens the KYC
  step here into a full pipeline: document checks, sanctions
  screening workflow, and case handling. This repo keeps only the
  boolean KYC gate a memo needs.
- **Finance compliance RAG (planned companion).** Retrieval over
  policy documents to ground compliance answers. This repo's
  rulebook is a small static table; the companion handles document
  retrieval at scale.
- **Finance fraud detection (existing portfolio area).** Transaction
  and ring detection. Fraud signals are deliberately out of scope
  here: a credit memo judges one application, not a network.
- **Finance governance proof-of-concept (planned companion).** The
  audit trail, model-risk register, and approval governance around
  systems like this one. This repo's approval gate is the control the
  companion would govern.

Where behaviour overlaps (approval gates, PII redaction, authorizer
patterns), the shared conventions are the portfolio repo standard:
named-person single-use approvals, card + email redaction, and
runtime denial proofs. No code is copied between repos without its
tests.
