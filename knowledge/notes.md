# Knowledge notes — distilled patterns

Distilled in the author's own words from a published program brochure
on AI in finance. No source sentences are reproduced here; see the
README's source note for the overlap-check result.

## Patterns worth keeping

### 1. Split the decision, then synthesise it

A credit decision is not one judgement but several: risk, policy fit,
identity, and explanation. Running each as its own step — with its
own output shape — makes the final memo checkable. If the memo only
ever saw a single score, no reviewer could tell which step failed.
This repo keeps the steps separate and carries each step's output
into the memo verbatim.

### 2. Explanations must add up

An explanation that does not reconcile to the decision is decoration.
Here the per-feature contributions sum exactly to the score minus
the base, because the scorer uses integer arithmetic and refuses to
clamp. The design lesson generalises: pick a scoring form whose
explanation is an identity, not an approximation, whenever the
decision will be reviewed.

### 3. Policy as cited rules, not vibes

A memo that says "this fits policy" proves nothing. A memo that says
"rule POL-01, section 3.1, met" gives the reviewer something to
verify. Citing rules by id and section turns the memo into an audit
artifact instead of a narrative.

### 4. Identity before decision

KYC is a gate, not a footnote. In this pipeline a failed identity
check forces Decline before any risk discussion matters, because a
decision about the wrong person is worse than no decision.

### 5. Human approval is a state change, not a comment

Finalising a memo is the one irreversible step in the pipeline, so it
is the one step a person must own by name, once, for one memo, before
a deadline. Everything else agents may draft; this step they may not.

### 6. Guardrails belong at the layer that cannot be skipped

Filtering PII in application code fails when a caller forgets.
Denying base-table reads in the database authorizer fails closed no
matter who calls. The same logic puts consent validation in the gate
itself, not in the caller that requests approval.

## What was deliberately NOT copied

- No real loan records, no real borrower attributes, no real policy
  wording. The brochure's case material describes real-data work;
  this repo re-implements the pattern on invented data.
- No institutional claims. Nothing here suggests endorsement by, or
  affiliation with, any university, provider, or lender.
