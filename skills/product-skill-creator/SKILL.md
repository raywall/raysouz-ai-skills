---
name: product-skill-creator
description: Analyze one or more repositories that implement a product, trace behavior across distributed systems, and create or refresh an evidence-backed product skill containing product purpose, domains, actors, processes, journeys, functional requirements, business logic, business rules, integrations, data ownership, vocabulary, risks, and open gaps. Use when asked to absorb how a product works from code, generate a reusable product/domain skill, consolidate knowledge across repositories or services, or update an existing product skill after repositories change.
---

# Product Skill Creator

Create a reusable product skill from repository evidence. Treat repositories as
implementation evidence, not as the product boundary. A product may span
frontends, APIs, workers, databases, infrastructure, events, and third-party
integrations across several repositories.

## Modes

- `create`: analyze repositories and create a new product skill.
- `refresh`: update an existing product skill from repository changes.
- `audit`: assess coverage, freshness, contradictions, and gaps without rewriting
  confirmed product knowledge.

Infer `create` only when no product skill exists. Otherwise use `refresh`, unless
the user explicitly requests `audit`.

## Non-Negotiable Rules

1. Base product facts on traceable evidence. Never turn a plausible inference
   into a business rule.
2. Label every statement as `CONFIRMED`, `INFERRED`, `PROPOSED`, or `GAP` when
   its certainty is not obvious.
3. Use code, tests, schemas, API contracts, event definitions, configuration,
   documentation, and approved user input as evidence.
4. Do not copy secrets, credentials, personal data, production records, or
   sensitive internal URLs into generated skills.
5. Trace representative journeys end to end before defining domains.
6. Separate product behavior from current implementation. Document both, but do
   not mistake controllers, folders, repositories, or tables for domains.
7. Preserve contradictions instead of silently choosing one implementation.
8. A generated product skill must help future agents analyze, implement, review,
   test, and improve the product, not merely describe its architecture.
9. In `refresh`, preserve confirmed knowledge unless new evidence contradicts it;
   record the contradiction and request validation.
10. Do not modify analyzed product repositories unless the user separately asks
    for implementation work.

## Required Workflow

### 1. Scope and Evidence

Read and execute [operations/01-scope-and-inventory.md](operations/01-scope-and-inventory.md).

Run:

```bash
python3 scripts/inventory_repositories.py \
  --product "<product-name>" \
  --output /tmp/product-inventory.json \
  <repo-path> [<repo-path> ...]
```

Establish the product objective, repositories, output skill path, approved
sources, analysis depth, and known vocabulary. Discover additional repositories
from integrations, but do not clone or include them without approval.

### 2. Discover Product and Domains

Read and execute [operations/02-product-and-domain-discovery.md](operations/02-product-and-domain-discovery.md).
Read [references/evidence-and-confidence.md](references/evidence-and-confidence.md)
and [references/distributed-product-analysis.md](references/distributed-product-analysis.md).

Build a product map from user outcomes, actors, capabilities, decisions, data
authority, and change reasons. Classify domains only after tracing behavior.

### 3. Trace Behavior and Requirements

Read and execute [operations/03-behavior-and-requirements.md](operations/03-behavior-and-requirements.md).
Use [templates/evidence-register.md](templates/evidence-register.md) and
[templates/product-analysis.md](templates/product-analysis.md).

Extract:

- product purpose, actors, outcomes, and constraints;
- business processes and end-to-end journeys;
- functional requirements and acceptance outcomes;
- business logic, calculations, validations, state transitions, and invariants;
- business rules, exceptions, timing, authorization, and failure behavior;
- repositories, systems, integrations, events, data ownership, and dependencies;
- glossary, contradictions, risks, and gaps.

### 4. Generate or Refresh the Product Skill

Read and execute [operations/04-generate-and-validate.md](operations/04-generate-and-validate.md).
Use [templates/generated-product-skill.md](templates/generated-product-skill.md)
and the reference templates under `templates/generated-references/`.

The generated skill must use progressive disclosure:

```text
<product-skill>/
├── SKILL.md
├── product-manifest.json
└── references/
    ├── product-overview.md
    ├── domains-and-contexts.md
    ├── processes-and-journeys.md
    ├── functional-requirements.md
    ├── business-rules.md
    ├── system-landscape.md
    ├── data-and-integrations.md
    ├── glossary.md
    └── gaps-and-decisions.md
```

Validate:

```bash
python3 scripts/validate_product_skill.py <generated-product-skill>
python3 scripts/scan_artifacts.py <generated-product-skill>
```

## Analysis Strategy

Explore repositories in parallel for structural inventory and focused reads.
Perform end-to-end synthesis centrally so cross-repository behavior remains
coherent.

Prioritize evidence in this order:

1. executable tests and acceptance scenarios;
2. domain/application logic and state machines;
3. schemas, constraints, migrations, and contracts;
4. entry points, UI flows, workers, events, and integrations;
5. documentation, comments, and user-facing messages;
6. git history and approved stakeholder input.

Use lower-priority evidence to explain intent, not to override executable
behavior without recording a contradiction.

## Refresh Strategy

Compare each repository's current commit with `product-manifest.json`.

- Reanalyze changed journeys, contracts, rules, and owned data.
- Revalidate downstream impacts when an event or API contract changes.
- Mark stale knowledge when a referenced repository is unavailable.
- Update `last_verified` and evidence references only after verification.
- Keep a concise change-impact section in `gaps-and-decisions.md`.

## Quality Gate

Do not finish until:

- every confirmed business rule has evidence;
- every representative journey reaches terminal outcomes;
- domains have purpose and ownership, not only technical labels;
- cross-repository boundaries and contracts are explicit;
- product behavior and implementation detail are separated;
- contradictions and unknowns are visible;
- the generated skill tells future agents how to use the knowledge during
  implementation and review;
- validation and sensitive-artifact scanning pass.

