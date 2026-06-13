---
name: software-factory-orchestrator
description: Orchestrate an evidence-backed low-code software delivery pipeline from repository analysis through functional specification, DDD context and service design, AWS Go implementation, GraphQL connector generation, business-rule simulation, and routing-slip workflow generation. Use when a request spans multiple software-engineering-skills stages or asks to transform analyzed business behavior into a new solution.
---

# Software Factory Orchestrator

Coordinate the suite without collapsing discovery, design, and implementation
into one unreviewable step.

## Required Context

Read `../contracts/artifact-contracts.md`. When starting from repositories, run
`business-capability-analysis` first. Never treat repositories as service
boundaries.

## Workflow

1. Determine requested scope, target stage, target AWS runtime, and confirmed
   decisions. Infer only reversible choices.
2. Initialize the workspace:

   ```bash
   python3 ../scripts/init_factory.py \
     --name "<name>" \
     --analysis <analysis-directory> \
     --output <output-parent>
   ```

3. Run stages in order unless valid prior-stage artifacts already exist:
   - `functional-specification-author`
   - `domain-context-designer`
   - `aws-service-code-generator` for each approved `SVC-*`
   - `graphql-connector-generator` for read/enrichment facades
   - `business-rule-simulator` for executable decision scenarios
   - `routing-slip-application-generator` for orchestration workflows
4. At every handoff, preserve source IDs and keep `INFERRED`, `GAP`, and
   `PROPOSED` visible.
5. Update `factory-manifest.json` stage status and artifact paths.
6. Validate the completed stage with `../scripts/validate_factory.py`.

## Routing Rules

- Stop after functional/domain design when boundaries or rules need stakeholder
  decisions.
- Generate code only from one approved service blueprint at a time.
- Use GraphQL connector for anticorruption/read enrichment, not business
  mutations.
- Use Business Rules scripts to make decisions and calculations inspectable.
- Use routing-slip for cross-step orchestration, idempotency, reprocessing, and
  controlled side effects.

## Quality Gate

Reject a handoff when traceability is absent, a service owns data from multiple
contexts, inferred behavior is presented as confirmed, or generation would
require inventing framework APIs.
