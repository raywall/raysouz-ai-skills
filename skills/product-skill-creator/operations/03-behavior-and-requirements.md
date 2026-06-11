# Operation 03 - Behavior and Requirements

## Select Representative Journeys

Cover at least:

- the primary value-producing journey;
- one administrative or configuration journey;
- one asynchronous or integration-heavy journey when present;
- one failure, reversal, cancellation, or exception journey;
- one reporting or consultation journey when present.

## Trace Each Journey

Follow the behavior across all relevant repositories and systems:

1. trigger and actor;
2. authorization and preconditions;
3. input and validation;
4. decisions, calculations, and state transitions;
5. persistence and authoritative owner;
6. synchronous and asynchronous boundaries;
7. retries, idempotency, errors, and compensations;
8. terminal outcomes and user-visible effects.

Record every step with evidence IDs. Use diagrams for complex flows.

## Extract Requirements

Write functional requirements as observable outcomes:

```text
FR-###: When <trigger/precondition>, the product shall <observable behavior>,
resulting in <outcome>.
```

Write business rules as decisions or invariants:

```text
BR-###: <rule>. Applies when <scope>. Exceptions: <exceptions>.
Evidence: <IDs>. Confidence: <level>.
```

Separate:

- functional requirement: what the product must do;
- business rule: decision or invariant controlling behavior;
- business logic: implementation-independent procedure or calculation;
- technical constraint: current implementation or platform limitation;
- proposal: desired future behavior.

## Contradictions

When implementations disagree:

- preserve each observed behavior;
- identify affected repositories and journeys;
- mark the intended rule as `GAP`;
- do not silently normalize the generated skill.

