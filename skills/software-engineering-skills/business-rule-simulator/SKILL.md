---
name: business-rule-simulator
description: Generate executable Business Rules Studio YAML scripts and scenario matrices from functional specifications, use cases, business rules, data contracts, or domain models. Use to simulate decisions, calculations, validations, alternate outcomes, and linked cross-service use cases before or alongside implementation.
---

# Business Rule Simulator

Read `references/script-contract.md`. Inspect
`/Users/raysouz/Workspace/estudos/business-rules-plugin/INSTRUCTIONS.md` and
representative `studio/examples` or `studio/workspace` files before generation.

## Procedure

1. Select one `UC-*` or cohesive decision process per YAML script.
2. Map external inputs to `input`, reads to editable `mocks`, validations and
   decisions to CEL `condition`, calculations to `compute`, and terminal
   outcomes to `result`.
3. Preserve rule IDs in descriptions and make rejection messages business
   meaningful.
4. Use `links` only for cross-service/use-case continuation.
5. Generate under `50-simulations/<context>/`:
   - one YAML per use case
   - `scenario-matrix.md` covering success, rejection, boundary, duplicate,
     and external-data variants
   Use `../templates/scenario-matrix.md` as the scenario base.
6. Use synthetic, non-sensitive examples and globally unique script IDs.
7. Validate YAML syntax and manually inspect CEL references for variables loaded
   before use.

## Constraints

- Simulations explain and test behavior; they are not production authorization.
- Keep uncertain rules marked in descriptions and scenario expectations.
- Do not place real credentials, personal data, or production payloads in mocks.
- Prefer decimal numeric examples for CEL numeric compatibility.
