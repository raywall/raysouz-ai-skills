---
name: business-capability-analysis
description: Analyze one or more repositories to explain the current business and solution in depth, including structure, domain models, business capabilities, end-to-end processes, business logic, rules, data ownership, integrations, risks, and improvement opportunities. Use for codebase analysis, reverse engineering, business understanding, capability mapping, architecture assessment, monolith decomposition discovery, modernization planning, or rearchitecture preparation.
---

# Business Capability Analysis

Produce an evidence-backed current-state analysis that explains both **what the
business does** and **how the solution currently enables it**. Treat repositories
and services as implementation evidence, not as business boundaries.

This skill creates analysis and opportunities. It does not implement changes or
present a proposed target architecture as current fact.

## Modes

- `landscape`: broad analysis of the business and solution. Default for broad
  requests.
- `focused`: deep trace of a named capability, process, rule, or journey.
- `refresh`: update an existing analysis from repository changes.
- `assessment`: emphasize risks and opportunities using an existing or newly
  generated current-state model.

## Non-Negotiable Rules

1. Keep every important claim traceable to evidence.
2. Mark uncertain statements as `INFERRED`, unknown or contradictory statements
   as `GAP`, and recommendations as `PROPOSED`.
3. Separate business behavior from technical implementation.
4. Trace representative journeys before finalizing domains or capabilities.
5. Do not assume one repository, service, module, controller, or table equals one
   domain or capability.
6. Preserve contradictory implementations and identify affected journeys.
7. Distinguish authoritative data ownership from read access and shared storage.
8. Analyze frontend, backend, workers, tests, schemas, infrastructure, and
   integrations when present; business logic may live anywhere.
9. Never copy secrets, credentials, personal data, production records, or
   sensitive internal URLs into artifacts.
10. Do not modify analyzed repositories unless the user separately requests
    implementation.

## Required Workflow

### 1. Scope and Inventory

Read and execute [operations/01-scope-and-inventory.md](operations/01-scope-and-inventory.md).

Run:

```bash
python3 scripts/inventory_codebases.py \
  --analysis-name "<name>" \
  --output /tmp/business-analysis-inventory.json \
  <repo-path> [<repo-path> ...]
```

For a new analysis, scaffold the output:

```bash
python3 scripts/init_analysis.py \
  --name "<name>" \
  --output <parent-directory> \
  --inventory /tmp/business-analysis-inventory.json
```

### 2. Discover Structure and Landscape

Read and execute [operations/02-structure-and-landscape.md](operations/02-structure-and-landscape.md).
Read [references/analysis-heuristics.md](references/analysis-heuristics.md).

Map deployables, entry points, layers, interfaces, storage, tests,
infrastructure, dependencies, and missing systems.

### 3. Extract Domains and Capabilities

Read and execute [operations/03-domains-and-capabilities.md](operations/03-domains-and-capabilities.md).
Read [references/domain-and-capability-modeling.md](references/domain-and-capability-modeling.md).

Extract business vocabulary, actors, outcomes, domain models, aggregate
candidates, bounded-context candidates, and business capabilities.

### 4. Trace Processes, Logic, and Rules

Read and execute [operations/04-processes-logic-and-rules.md](operations/04-processes-logic-and-rules.md).

Trace representative journeys from trigger to terminal outcomes across all
relevant repositories. Extract validations, calculations, decisions, state
transitions, edge cases, errors, authorization, timing, and configuration-driven
behavior.

### 5. Map Integrations and Data

Read and execute [operations/05-integrations-and-data.md](operations/05-integrations-and-data.md).
Read [references/distributed-systems-analysis.md](references/distributed-systems-analysis.md).

Map APIs, events, queues, files, jobs, databases, shared stores, third parties,
data authority, consistency, idempotency, retries, and failure handling.

### 6. Assess Risks and Opportunities

Read and execute [operations/06-risks-and-opportunities.md](operations/06-risks-and-opportunities.md).
Read [references/opportunity-assessment.md](references/opportunity-assessment.md).

Identify opportunities for:

- business-process simplification and automation;
- domain model and rule centralization;
- reliability, security, testing, observability, and performance;
- reducing coupling and clarifying ownership;
- incremental monolith decomposition;
- rearchitecture and modernization.

Keep opportunities evidence-based and separate from current facts.

### 7. Synthesize and Validate

Read and execute [operations/07-synthesis-and-validation.md](operations/07-synthesis-and-validation.md).
Use [templates/output-catalog.md](templates/output-catalog.md) and
[templates/analysis-templates.md](templates/analysis-templates.md).

Validate:

```bash
python3 scripts/validate_analysis.py <analysis-directory>
python3 scripts/scan_artifacts.py <analysis-directory>
```

## Output

Generate `_business-capability-analysis/` with:

- executive summary and scope;
- evidence register;
- system structure and current architecture;
- domain model and context candidates;
- capability map;
- business processes and journeys;
- business logic and rules;
- integration map and data ownership;
- risks and opportunity assessment;
- gaps, decisions, and traceability matrix.

## Evidence Priority

Prioritize:

1. executable tests and acceptance scenarios;
2. domain/application logic and state machines;
3. schemas, constraints, migrations, and contracts;
4. UI flows, APIs, workers, events, jobs, and reports;
5. documentation, user-facing messages, configuration, and comments;
6. git history and approved stakeholder input.

Lower-priority evidence may explain intent but must not silently override
executable behavior.

## Quality Gate

Do not finish until:

- representative journeys reach success and failure terminal outcomes;
- domains and capabilities have business purpose and evidence;
- important rules have stable IDs and evidence;
- cross-system contracts and data owners are explicit;
- current facts, inferences, gaps, and proposals are separated;
- opportunities identify evidence, expected value, dependencies, risk, and
  validation needed;
- validation and sensitive-artifact scanning pass.

