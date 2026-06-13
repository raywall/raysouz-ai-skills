---
name: aws-service-code-generator
description: Generate production-oriented Go service code, tests, contracts, observability, and infrastructure as code from an approved service blueprint for a specified AWS runtime such as Lambda or ECS Fargate. Use when implementing one bounded-context service from functional and domain specifications.
---

# AWS Service Code Generator

Apply `go-clean-architecture`, `go-microservices-aws`, `go-doc-standards`,
`go-testing-excellence`, and `observability-finops` when available.
Read `../contracts/artifact-contracts.md` and `references/aws-generation.md`.

## Inputs

Require one approved `service-blueprint.yaml`, its acceptance criteria and
contracts, plus an explicit AWS compute target. Ask only when an irreversible
or materially costly choice is missing.

## Procedure

1. Verify the service owns one context and every behavior traces to source IDs.
2. Inspect the target repository and installed framework APIs before generating.
3. Select Lambda for sparse/event-driven stateless work; ECS Fargate for
   sustained traffic, long-running processes, or long-lived connections.
4. Generate under `40-generated/<service>/`:
   - Go clean-architecture implementation
   - inbound/outbound adapters and contracts
   - unit, integration, contract, and acceptance tests
   - IaC using the repository's existing tool or Terraform by default
   - configuration, observability, security, and operational notes
   - `generation-report.md` with implemented IDs, gaps, and verification
5. Implement idempotency, retries, timeout, DLQ/outbox, and partial-batch
   behavior where the blueprint requires them.
6. Compile, test, format, validate IaC, and scan for secrets.

## Constraints

- Never implement `INFERRED` or `GAP` behavior as confirmed logic.
- Keep domain packages independent from AWS SDK and transport types.
- Do not invent framework APIs; inspect local modules and versions.
- Do not generate a distributed transaction across service boundaries.
