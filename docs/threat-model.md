# Threat model

## Assets

- Synthetic application data (no real PII, but the code paths must
  behave as if it were sensitive — the same redaction and view rules
  would protect real data).
- Credit memos and their approval state (integrity matters: a memo
  must not become FINAL without approval).
- The rulebook and scorer (integrity matters: silently changed
  thresholds would change decisions).

## STRIDE

| Threat | Mitigation in this repo | Residual risk |
| --- | --- | --- |
| Spoofing an approver | Approvals name one person; a different name raises `WrongApprover` | Approver names are strings, not authenticated identities — a real deployment needs identity proof |
| Tampering with a memo's status | Only the gate path sets FINAL, and it requires an accepted decision | In-memory gate state is not shared across processes |
| Repudiation of an approval | Token, approver, scope, and expiry are recorded on the decision | No append-only audit log yet — planned |
| Information disclosure (PII) | View-only authorizer, PII-free views, redaction sweep on memo text, logs, and errors | PII fields exist on the model as test fixtures; a future caller could misuse them |
| Denial of service (unbounded reads) | Row cap via `fetchmany(MAX+1)` fails loudly on overflow | No per-caller rate limiting |
| Elevation via the database | Authorizer denies writes, PRAGMA, ATTACH, DROP, and extension loading | SQLite file access itself is out of scope here (in-memory demo) |

## LLM-specific notes (OWASP LLM Top 10, where relevant)

- **Prompt injection:** no language model is called in this
  scaffold, so there is no prompt surface. If a narration model is
  added later, it must receive only cited facts and redacted text,
  never raw application rows.
- **Excessive agency:** the pipeline takes no external action. The
  only state change (DRAFT → FINAL) requires human approval.
- **Sensitive information disclosure:** covered by the redaction and
  view layers above; narration output would need the same sweep.

## ADRs

See [adr.md](adr.md).
