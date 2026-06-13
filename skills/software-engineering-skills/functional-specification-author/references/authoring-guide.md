# Functional Authoring Guide

## Functional Specification Sections

1. Scope, business objective, actors, assumptions, exclusions.
2. Capability and journey coverage.
3. Use cases with trigger, preconditions, main flow, alternate flows, terminal
   outcomes, rules, and data.
4. Functional and non-functional requirements.
5. State transitions and timing constraints.
6. External interactions stated as business needs.
7. Gaps, contradictions, and decisions.

## Acceptance Scenario Shape

Use `Given / When / Then` and include IDs:

```text
SCN-001 | UC-001 | BR-VAL-001
Given ...
When ...
Then ...
And ...
```

Cover valid, invalid, boundary, duplicate, timeout, retry, and partial-failure
cases when applicable.

## Data Contract Shape

For each `DATA-*`, document purpose, producer, consumers, fields, semantic
constraints, sensitivity, lifecycle, authoritative source, and source IDs.
