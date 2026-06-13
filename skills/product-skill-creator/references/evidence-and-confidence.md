# Evidence and Confidence

## Evidence Record

Each evidence record should contain:

| Field | Meaning |
|---|---|
| ID | Stable `EVD-###` identifier |
| Repository | Repository name |
| Source | Relative path plus symbol or line when useful |
| Type | test, code, schema, contract, config, docs, history, user |
| Observation | What is directly observable |
| Supports | IDs of rules, requirements, journeys, or domains |
| Commit | Commit used during verification |

## Confidence

- `CONFIRMED`: directly evidenced and internally consistent.
- `INFERRED`: likely explanation assembled from evidence, not explicitly proven.
- `PROPOSED`: recommendation or target state, not current behavior.
- `GAP`: unknown, contradictory, missing, or requiring owner validation.

## Rules

- Prefer several small evidence records over one vague record.
- Cite observations, not secrets or raw business data.
- A comment stating intent does not override contradictory executable behavior.
- Absence of code is not proof that a behavior does not exist in another system.
- User confirmation may establish business intent; retain contrary implementation
  evidence as technical debt or behavior mismatch.

