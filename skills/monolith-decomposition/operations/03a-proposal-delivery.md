# Operation 03A - Proposal Delivery

Use this operation only in `propose` mode.

1. Produce a complete decomposition plan from `templates/decomposition-plan.md`.
2. Include Mermaid diagrams for current architecture, business logic, business
   rules, domain/context map, target architecture, and transition stages.
3. Define domains, subdomains, bounded contexts, responsibilities, dependencies,
   contracts, and boundary alternatives.
4. Include database split options and a recommendation when data ownership changes.
5. Include the recommended transition pattern, sequencing, tests, observability,
   rollback, risks, decisions, and unresolved gaps.
6. Mark target architecture and transition choices as proposals until approved.
7. Run sensitive-artifact scanning and request review.
8. Validate `proposal` readiness after the sensitive-data review.
9. Stop. Do not generate services, modify the monolith, or execute migration.

The proposal must be actionable enough for a later `operate` engagement.
