---
name: graphql-connector-generator
description: Generate a working go-graphql-connector application from data and integration specifications, including config/service.json, config/schema.json, config/connectors.json, connector.go, queries, tests, and runtime-specific bootstrap for local, Lambda, or ECS deployment. Use for read aggregation, enrichment, and anticorruption facades.
---

# GraphQL Connector Generator

Apply `go-graphql-connector-builder`. Read
`references/generation-contract.md`. Inspect the installed
`go-graphql-connector` examples and package APIs before writing `connector.go`.

## Inputs

Require logical data contracts, integration sources, desired GraphQL query
shape, configuration source (`local`, environment, SSM, Secrets Manager, S3, or
DynamoDB), and runtime (`local`, `lambda-alb`, `lambda-api-gateway`, or `ecs`).

## Procedure

1. Confirm this is a read/enrichment facade; route commands elsewhere.
2. Map logical models to GraphQL types and source calls to connector fields.
3. Generate:
   - `config/service.json`
   - `config/schema.json`
   - `config/connectors.json`
   - optional `config/mock.json`
   - `connector.go`
   - GraphQL query/request examples and tests
4. Keep field names aligned between the `dataSources` output type and
   `connectors.json`.
5. Configure unwrap/error paths, timeout, retries, partial response, token
   authorization, and resilience from source characteristics.
6. Use environment/secret references; never embed credentials.
7. Run formatting, compilation, tests, and JSON validation.

## Constraints

- Use `github.com/raywall/go-graphql-connector/graphql` and the installed
  exported API, not invented constructors.
- Preserve source `INT-*`, `DATA-*`, `QRY-*`, and `SVC-*` traceability.
- Add health routing and graceful shutdown appropriate to the target runtime.
