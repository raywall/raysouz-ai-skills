# Artifact Contracts

## Principles

- Preserve source IDs and evidence links through every stage.
- Separate `CONFIRMED`, `INFERRED`, `GAP`, and `PROPOSED`.
- Never silently turn an inference or proposal into implemented behavior.
- Prefer technology-neutral functional artifacts before target architecture.
- Generate one deployable only after its business responsibility and data
  ownership are explicit.

## Workspace

| Stage | Directory | Required artifacts |
|---|---|---|
| analysis | external input | `_business-capability-analysis/` |
| functional | `10-functional/` | `functional-specification.md`, `acceptance-scenarios.md`, `data-contracts.md`, `traceability-matrix.md` |
| domain | `20-domain/` | `domain-landscape.md`, `context-map.md`, `model-catalog.md`, `service-catalog.md`, `traceability-matrix.md` |
| services | `30-services/<service>/` | `service-blueprint.yaml`, `acceptance-criteria.md`, `contracts/`, `traceability.md` |
| generated | `40-generated/<service>/` | implementation, tests, IaC, `generation-report.md` |
| simulation | `50-simulations/<context>/` | Business Rules YAML scripts and `scenario-matrix.md` |
| workflow | `60-workflows/<service>/` | routing-slip workflow/config/app and test payloads |

## Functional IDs

- `FR-*`: functional requirement.
- `NFR-*`: non-functional requirement.
- `UC-*`: use case.
- `SCN-*`: acceptance scenario.
- `DATA-*`: logical data concept or contract.
- Reuse source `CAP-*`, `JRN-*`, `BR-*`, `INT-*`, `GAP-*`, and `EVD-*`.

Every `FR-*` must reference at least one capability or journey and one source
rule/evidence or explicit stakeholder decision.

## Domain IDs

- `DOM-*`: subdomain.
- `CTX-*`: bounded context.
- `AGG-*`: aggregate.
- `ENT-*`: entity.
- `VO-*`: value object.
- `EVT-*`: domain event.
- `CMD-*`: command.
- `QRY-*`: query.
- `SVC-*`: independently deployable service candidate.

Every aggregate lists invariants, commands, events, owned data, and source
requirements/rules. Every service blueprint names exactly one owning context.

## Service Blueprint Minimum

```yaml
schema_version: "1.0"
service:
  id: SVC-001
  name: example-service
  context_id: CTX-001
  purpose: ""
  runtime:
    aws_compute: lambda
    language: go
  inbound: []
  outbound: []
  data_ownership: []
  use_cases: []
  business_rules: []
  domain_models: []
  quality_attributes: []
  observability: []
  security: []
  decisions: []
  gaps: []
  traceability: []
```

Allowed `aws_compute`: `lambda`, `ecs-fargate`, `eks`, or `undecided`.

## Quality Gates

1. Functional: scenarios cover success, rejection, failure, and important edge
   cases; contradictions remain visible.
2. Domain: contexts have explicit ownership and integration relationships;
   invariants are assigned to aggregates or domain services.
3. Service: runtime and AWS resources are justified; contracts, idempotency,
   failure handling, security, observability, and tests are specified.
4. Generation: code compiles, tests pass, IaC validates, secrets are external,
   and all implemented rules link back to source IDs.
