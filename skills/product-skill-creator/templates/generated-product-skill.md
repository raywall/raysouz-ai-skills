---
name: <product-skill-name>
description: Provide evidence-backed product, domain, process, functional-requirement, business-logic, and business-rule context for <product>. Use whenever analyzing, implementing, reviewing, testing, debugging, or improving repositories and systems that participate in <product>, especially work involving <domains/journeys>.
---

# <Product> Product Context

Load this skill before changing product behavior. Repositories are implementation
parts of the product; check cross-system impact before editing.

## Required Use

1. Identify affected domain, journey, actor, and repositories.
2. Read the relevant references listed below.
3. Check applicable functional requirements, business rules, gaps, and
   contradictions.
4. Trace upstream and downstream contracts before changing behavior.
5. Preserve confirmed invariants and add tests for changed rules.
6. State affected domains/systems, assumptions, and unresolved gaps in the final
   summary.

Never invent an undocumented product rule. Mark uncertainty and request the
required source or owner.

## Product Snapshot

- Purpose: <summary>
- Core outcomes: <outcomes>
- Core domains: <domains>
- Current repositories: <repositories>
- Last verified: <timestamp>

## References

- `references/product-overview.md`
- `references/domains-and-contexts.md`
- `references/processes-and-journeys.md`
- `references/functional-requirements.md`
- `references/business-rules.md`
- `references/system-landscape.md`
- `references/data-and-integrations.md`
- `references/glossary.md`
- `references/gaps-and-decisions.md`

