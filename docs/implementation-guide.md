# Implementation guide (for adopters)

## Install

No dependencies. Python 3.10+ and pytest for the suite:

```bash
python3 -m pytest tests/ -q
```

## Use the pipeline

```python
from credit_memo.pipeline import run_pipeline, finalize_with_approval
from credit_memo.approval import ApprovalGate
from credit_memo.samples import CLEAN_KYC, SAMPLES

result = run_pipeline(SAMPLES[0], CLEAN_KYC, "MEMO-001")
memo = result["memo"]  # status DRAFT, recommendation + rationale inside

gate = ApprovalGate()
req = gate.request(memo_id="MEMO-001", approver="Priya Nair")
final = finalize_with_approval(memo, gate, req.token, "Priya Nair",
                               "yes, approved", 0.9)
```

## Adapt the rulebook

Edit `RULES` in `credit_memo/policy.py`: each rule needs a unique id,
a rulebook section, a severity (`hard` or `compensating`), and a
check function over an `Application`. Keep the recommendation logic
in `credit_memo/memo.py` in sync: hard failures decline,
compensating failures refer.

## Adapt the scorer

Edit `FEATURES` in `credit_memo/scorer.py`. Keep the invariant
`score == BASE_SCORE + sum(contributions)` — do not clamp the score,
or the explainability claim breaks. The suite's sum-identity test
will catch a break immediately.

## Read through the store

```python
from credit_memo.store import open_store
from credit_memo.fetching import fetch_capped

conn = open_store()
rows = fetch_capped(conn.cursor(),
                    "SELECT * FROM v_application_metrics", max_rows=100)
```

Never query the base tables through this connection; the authorizer
will deny it, by design. If you need a writer, build a separate
service with its own authentication — do not relax this authorizer.

## Add a blocked name

```python
from credit_memo.brand import add_blocked_name
add_blocked_name("Some Real Firm")
```

Names are stored as hashes only. Run `python3 tools/brand_check.py .`
before shipping docs.

## Email

`EmailChannel` is dry-run by default and has no transport. If you add
a transport, keep the opt-in requirement and the CI refusal, and keep
credentials out of the repo.
