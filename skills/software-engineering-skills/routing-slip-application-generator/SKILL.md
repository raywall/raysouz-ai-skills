---
name: routing-slip-application-generator
description: Generate routing-slip-pattern workflow YAML, config.yaml, Go runtime bootstrap, test payloads, and deployment artifacts from functional specifications, business rules, integrations, and service blueprints. Use for executable orchestration, event processing, enrichment, controlled side effects, idempotency, reprocessing, and observable multi-step workflows.
---

# Routing Slip Application Generator

Apply `routing-slip-workflow-author` and `routing-slip-runtime-bootstrap`.
Apply `workflow-ecosystem-architecture` when GraphQL connector or business
metrics are included. Read `references/generation-contract.md` and inspect the
installed routing-slip package APIs before generating Go code.

## Procedure

1. Select one end-to-end journey or service-owned process.
2. Map validation, decisions, calculations, enrichment, effects, and audits to
   supported handlers.
3. Use `graphql_enrich` for read aggregation and ACL; use `rest_call` or
   `aws_action` for effects.
4. Split long flows with `workflow_ref` while preserving message and correlation
   IDs.
5. Generate under `60-workflows/<service>/`:
   - `config.yaml`
   - `workflows/*.yaml`
   - real `main.go` or Lambda bootstrap against inspected APIs
   - payloads/events and regression scenarios
   - deployment/local-run artifacts when requested
6. Configure state store, idempotency, processing lock, retries, observability,
   redaction, and reprocessing.
7. Validate YAML, execute representative scenarios, compile, and test.

## Constraints

- Every business decision step references `BR-*` or an explicit decision.
- Stable step IDs are mandatory.
- Side effects must be idempotent or explicitly guarded.
- Never invent exported framework APIs; inspect the target version.
- Keep service-owned workflows distinct from cross-context orchestration.
