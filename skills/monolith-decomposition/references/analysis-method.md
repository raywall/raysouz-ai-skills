# Language-Agnostic Monolith Analysis

## Analysis layers

Analyze the monolith in separate passes so technical structure is not mistaken for
domain structure.

### Repository and runtime

Identify modules, manifests, entry points, build commands, deployment units,
configuration sources, data stores, integrations, jobs, events, and test suites.

### Execution traces

Trace representative business journeys from entry point to terminal outcome.
For each trace, record evidence for:

- input and actor;
- validations and authorization;
- decision branches and defaults;
- state reads and writes;
- calculations and transformations;
- external calls and emitted events;
- errors, retries, compensations, and terminal outcomes.

### Business rules

A business rule is an evidenced condition that changes an allowed action, decision,
calculation, state transition, obligation, or outcome. Keep orchestration,
framework behavior, and infrastructure concerns separate from business rules.

### Domain discovery

Group evidenced vocabulary, rules, data ownership, and change reasons. Identify:

- core, supporting, and generic subdomains only when evidence supports the labels;
- bounded-context candidates with distinct language and responsibilities;
- aggregates and invariants;
- domain events and lifecycle states;
- existing coupling and shared-data dependencies.

### Change and risk

Use tests, incident records, version history, and approved operational documents to
identify volatile areas and migration risk. Do not infer business criticality from
code complexity alone.

## Traceability rule

Every domain term, rule, boundary justification, and migration acceptance criterion
must point to evidence IDs. When evidence conflicts, record the conflict and ask
for a decision before using it.

## Analysis completion gate

Analysis is ready for decomposition only when:

- representative journeys and terminal outcomes are traced;
- business rules and unresolved gaps are registered;
- data ownership and integration boundaries are mapped;
- existing tests and missing characterization coverage are known;
- the user confirms the discovered current-state model.
