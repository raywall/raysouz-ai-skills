# TDD and Regression Strategy

## Testing order

### Characterization tests

Before changing behavior, create tests that capture evidenced current outcomes,
including edge cases and known defects that must remain visible. A characterization
test describes what the monolith currently does; it does not declare that behavior
correct.

### Domain tests

For each approved service boundary, write tests around business decisions,
invariants, calculations, lifecycle transitions, and failure outcomes before
implementing the new domain behavior.

### Contract tests

Protect every extracted boundary with consumer/provider contract tests. Contracts
must include error semantics, compatibility rules, and versioning expectations.

### Regression tests

Run old and new paths against approved sanitized fixtures or generated structural
fixtures whose expected outcomes come from registered evidence. Compare observable
business outcomes rather than internal implementation details.

### Migration tests

Test data transformation, replay, idempotency, rollback, cutover, and coexistence.
Do not use production personal data in test fixtures.

## Red-green-refactor

1. Write a failing test for one approved behavior.
2. Implement the smallest behavior that passes.
3. Refactor without changing observable outcomes.
4. Run the relevant characterization, contract, regression, and integration tests.
5. Record evidence and acceptance criteria satisfied by the change.

## Language selection

Use the target repository's existing test framework and conventions unless the user
approves a change. Generate tests in the requested language only after the target
stack and service boundary are confirmed.

## Completion gate

A slice is ready for migration only when:

- approved behavior has executable tests;
- regression comparison passes;
- contracts and ownership are documented;
- observability and rollback are verified;
- unresolved business gaps do not affect the slice.
