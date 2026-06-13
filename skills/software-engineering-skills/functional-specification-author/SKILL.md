---
name: functional-specification-author
description: Convert evidence-backed business capability analysis artifacts from one or more repositories into a technology-neutral functional specification with use cases, requirements, business rules, acceptance scenarios, data contracts, gaps, and end-to-end traceability. Use before domain separation, rearchitecture, replacement-system design, or code generation.
---

# Functional Specification Author

Translate observed behavior into an implementation-neutral contract for a new or
rearchitected solution.

## Inputs

Require `_business-capability-analysis/` or equivalent evidence-backed
artifacts. Read `../contracts/artifact-contracts.md` and
`references/authoring-guide.md`. Use `../templates/functional-specification.md`
as the base structure.

## Procedure

1. Select capabilities and journeys in scope. Record exclusions.
2. Convert current behavior into actors, triggers, preconditions, use cases,
   functional requirements, outcomes, and exception flows.
3. Preserve source business-rule IDs; split compound rules where needed.
4. Define logical data contracts and ownership needs without selecting a
   database or transport.
5. Write acceptance scenarios for success, rejection, failure, edge cases,
   duplicate/retry behavior, and contradictions.
6. Keep current behavior separate from desired changes. Assign new decisions
   IDs and mark proposals.
7. Produce under `10-functional/`:
   - `functional-specification.md`
   - `acceptance-scenarios.md`
   - `data-contracts.md`
   - `traceability-matrix.md`
8. Update the factory manifest and run:

   ```bash
   python3 ../scripts/validate_factory.py <workspace> --stage functional
   ```

## Constraints

- Do not choose bounded contexts, microservices, AWS resources, or code layout.
- Do not erase awkward current behavior; expose it as a decision or gap.
- Every `FR-*` and `SCN-*` must trace to source IDs or an explicit new decision.
- Express externally observable behavior, not current implementation mechanics.
