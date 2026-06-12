# Operation 04 - Processes, Logic, and Rules

## Select Journeys

In `landscape` mode, trace at least:

- primary value-producing journey;
- administrative or configuration journey;
- asynchronous or integration-heavy journey when present;
- failure, cancellation, reversal, or exception journey;
- reporting or consultation journey when present.

In `focused` mode, deeply trace the requested capability or process and all
material branches.

## Trace End to End

For each `JRN-###` journey, follow:

1. actor, trigger, and preconditions;
2. authorization and input;
3. validations and decisions;
4. calculations and transformations;
5. state transitions and persistence;
6. cross-system contracts;
7. retries, idempotency, timeout, fallback, and compensation;
8. success, failure, and alternate terminal outcomes.

## Extract Rules

Use stable IDs:

- `BR-VAL-###`: validation and eligibility;
- `BR-CALC-###`: calculations and derivations;
- `BR-DEC-###`: decisions, routing, and policy;
- `BR-STATE-###`: state transitions and lifecycle invariants;
- `EC-###`: valid edge cases;
- `ERR-###`: failure and rejection states.

For each rule, include scope, exceptions, evidence, confidence, affected
capabilities/journeys, and observed implementation locations.

## Detect Contradictions

When code paths disagree, preserve each observed behavior and create a `GAP-###`
for intended business behavior. Do not normalize silently.

