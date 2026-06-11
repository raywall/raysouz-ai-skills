# Output Catalog

Create only artifacts needed by the approved scope. Suggested workspace:

```text
docs/monolith-decomposition/
├── 00-clarifications.md
├── 01-evidence-register.md
├── 02-codebase-inventory.json
├── 03-current-state.md
├── 04-business-rules.md
├── 05-domain-model.md
├── 06-context-map.md
├── 07-decomposition-plan.md
├── 08-test-strategy.md
├── 09-migration-plan.md
├── 10-transition-architecture.md
├── services/
│   └── <service-name>.md
└── decisions/
    └── <decision>.md
```

## Required traceability

- Current-state statements cite evidence IDs.
- Business rules cite evidence IDs and affected journeys.
- Boundary proposals cite evidence and list open gaps.
- Service specifications cite approved boundary decisions.
- Tests cite the business rule or acceptance criterion they protect.
- Migration steps include validation and rollback criteria.
- Proposal mode includes all required Mermaid diagrams and a transition plan.

## Documentation audience

Separate internal working evidence from documents intended for broad distribution.
Remove restricted locators and sensitive implementation detail from broader
documents while preserving an approved internal traceability path.
