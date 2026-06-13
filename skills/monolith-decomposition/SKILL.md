---
name: monolith-decomposition
description: Use when tracing, understanding, documenting, or decomposing a monolithic codebase into microservices in any language using evidence-based Domain-Driven Design and Test-Driven Development. Triggers include monolith analysis, business-rule extraction, bounded-context discovery, decomposition by segment or capability, microservice extraction, characterization tests, regression tests, and migration planning.
---

# Monolith Decomposition

Analyze and incrementally decompose monoliths using approved corporate evidence,
DDD, and TDD. Preserve behavior deliberately and keep every business statement
traceable.

## Select a Mode First

Ask the user to select one mode before analysis:

- **`propose`**: analyze the monolith and deliver an actionable decomposition plan
  with Mermaid diagrams, domains, bounded contexts, business logic, business rules,
  database split strategy when needed, and a recommended transition architecture.
  Do not modify code or execute migration.
- **`operate`**: perform the analysis and approved decomposition incrementally,
  generating services, tests, documentation, and migration changes.

When the user's intent is unclear, ask. Never infer `operate`.

## Non-Negotiable Rules

1. Use only approved corporate sources available to the user. Do not fill business
   gaps with generic knowledge or assumptions.
2. Ask about doubts, gaps, scope, sources, vocabulary, decomposition axis,
   constraints, and acceptance criteria before decomposition begins.
3. Do not propose boundaries while a blocking gap could change them.
4. Separate established current-state facts, open gaps, and target design proposals.
5. Do not include personal data, credentials, secrets, sensitive internal URLs,
   accounts, raw production records, or restricted identifiers.
6. Do not generate a microservice until the user approves its boundary, target
   language, contracts, acceptance criteria, and extraction slice.
7. Use characterization and regression tests before replacing monolith behavior.
8. Stop and ask when new evidence contradicts an approved model or reveals a
   business gap.
9. In `propose` mode, stop after delivering the proposal. In `operate` mode,
   require explicit approval before every extraction slice.

## Required Workflow

### 1. Intake and Clarification Gate

Read and execute
[`operations/01-intake-and-evidence-gate.md`](operations/01-intake-and-evidence-gate.md).
Use [`templates/clarification-request.md`](templates/clarification-request.md),
[`templates/evidence-register.md`](templates/evidence-register.md), and
[`templates/decomposition-state.json`](templates/decomposition-state.json).

Do not begin decomposition until the user resolves blocking questions and confirms
the scope and approved sources.

Validate readiness:

```bash
python scripts/validate_readiness.py <state.json> --phase analysis
```

### 2. Trace and Understand the Monolith

Read and execute
[`operations/02-trace-and-domain-discovery.md`](operations/02-trace-and-domain-discovery.md).
Read [`references/evidence-policy.md`](references/evidence-policy.md) and
[`references/analysis-method.md`](references/analysis-method.md).

Create a content-free structural inventory first:

```bash
python scripts/inventory_codebase.py <monolith-root> --output <inventory.json>
```

Trace representative journeys end to end. Register evidence for domain vocabulary,
business decisions, calculations, validations, invariants, states, data ownership,
integrations, errors, and terminal outcomes. Present the current-state model for
user confirmation.

### 3. Design DDD Boundaries

After current-state confirmation, validate:

```bash
python scripts/validate_readiness.py <state.json> --phase decomposition
```

Read and execute
[`operations/03-decomposition-design.md`](operations/03-decomposition-design.md).
Use [`references/ddd-decomposition.md`](references/ddd-decomposition.md) and
[`references/transition-patterns.md`](references/transition-patterns.md), and
[`templates/decomposition-plan.md`](templates/decomposition-plan.md).

Use the user's requested decomposition axis. Boundaries must follow evidenced
business language, decisions, data authority, change reasons, and constraints.
Folders, framework layers, or database tables alone do not define a domain.

### 4. Finish Proposal or Operate

For `propose` mode, execute
[`operations/03a-proposal-delivery.md`](operations/03a-proposal-delivery.md), scan
the artifacts, validate proposal readiness, deliver the plan, and stop.

```bash
python scripts/scan_artifacts.py <generated-proposal>
python scripts/validate_readiness.py <state.json> --phase proposal
```

For `operate` mode, continue below.

### 5. Extract One Approved Slice with TDD

After boundary and target-stack approval, validate:

```bash
python scripts/validate_readiness.py <state.json> --phase implementation
```

Read and execute
[`operations/04-extraction-and-testing.md`](operations/04-extraction-and-testing.md).
Use [`references/tdd-migration.md`](references/tdd-migration.md),
[`templates/service-spec.md`](templates/service-spec.md), and
[`templates/test-plan.md`](templates/test-plan.md).

Use the target repository's approved language, architecture, test framework, and
conventions. Generate unit, contract, integration, regression, migration, and
rollback tests required by the approved slice.

### 6. Document and Hand Off

Read and execute
[`operations/05-documentation-and-handoff.md`](operations/05-documentation-and-handoff.md).
Use [`references/output-catalog.md`](references/output-catalog.md),
[`references/security-and-redaction.md`](references/security-and-redaction.md), and
[`templates/project-documentation.md`](templates/project-documentation.md).

Before publishing changes from `operate` mode:

```bash
python scripts/scan_artifacts.py <generated-artifacts>
python scripts/validate_readiness.py <state.json> --phase publish
```

Automated scanning does not replace an approved human security review.

## How to Respond to Gaps

When a required fact is missing:

1. Record a gap ID and its impact.
2. Ask a precise question and identify the expected corporate source or owner.
3. Continue only with work unaffected by the gap.
4. Do not create a generic definition, guessed rule, or speculative boundary.

Use [`examples/clarification-gate.example.md`](examples/clarification-gate.example.md)
and
[`examples/decomposition-by-segment.example.md`](examples/decomposition-by-segment.example.md)
only as format examples; their placeholders are not domain knowledge.
