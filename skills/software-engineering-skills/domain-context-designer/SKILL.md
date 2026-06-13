---
name: domain-context-designer
description: Separate a functional specification into DDD subdomains and bounded contexts, define ubiquitous language, aggregates, entities, value objects, invariants, commands, queries, domain events, context relationships, and independently deployable service blueprints. Use before microservice decomposition, AWS service implementation, or model generation.
---

# Domain Context Designer

Apply `ddd-context-mapping` before proposing deployables. Read
`../contracts/artifact-contracts.md` and `references/design-guide.md`. Use
`../templates/service-blueprint.yaml` for each approved service candidate.

## Procedure

1. Verify functional artifacts and source traceability.
2. Classify core, supporting, and generic subdomains.
3. Discover bounded contexts from language, decisions, invariants, lifecycle,
   data authority, and change cadence. Do not map contexts from repositories.
4. Define context relationships and anticorruption boundaries.
5. Model aggregates, entities, value objects, domain services, commands,
   queries, events, repositories, and invariants.
6. Assign each requirement and rule to one authoritative context.
7. Propose deployable `SVC-*` candidates only after contexts are stable.
8. Produce under `20-domain/`:
   - `domain-landscape.md`
   - `context-map.md`
   - `model-catalog.md`
   - `service-catalog.md`
   - `traceability-matrix.md`
9. Create `30-services/<service>/service-blueprint.yaml`,
   `acceptance-criteria.md`, `contracts/`, and `traceability.md` for each
   approved candidate.
10. Validate:

    ```bash
    python3 ../scripts/validate_factory.py <workspace> --stage domain
    ```

## Quality Rules

- One service blueprint owns exactly one bounded context.
- Keep one transaction within one aggregate; use events across aggregates.
- Identify shared database coupling as a migration problem, not target design.
- Mark uncertain boundaries as alternatives with a validation plan.
- Never create CRUD models without behaviors, invariants, and source rules.
