# Evidence-Based DDD Decomposition

## Boundary selection

Use the decomposition axis requested by the user. Examples include business
segment, capability, lifecycle, product, geography, regulatory boundary, or team.
Do not choose an axis solely because it is common practice.

For each bounded-context candidate, document:

- evidenced purpose and vocabulary;
- decisions and invariants it owns;
- authoritative data;
- actors and journeys;
- incoming and outgoing dependencies;
- reasons it changes;
- proposed owner, only if supplied or approved;
- evidence IDs and unresolved gaps.

## Boundary tests

A candidate boundary is stronger when evidence shows:

- cohesive business rules and language;
- independent reasons to change;
- clear data authority;
- limited synchronous coordination;
- independently testable outcomes;
- an extraction sequence that preserves behavior.

A candidate boundary is weaker when it is based only on folders, tables,
framework layers, or technical components.

## Context map

Map current and proposed relationships. Explicitly identify customer/supplier,
anti-corruption layer, published language, shared kernel, partnership, conformist,
or separate ways only when the relationship is evidenced or approved as a design
proposal.

## Service design

Do not assume every bounded context must become one microservice. For each proposed
service, justify:

- business capability and owned decisions;
- data ownership;
- API or event contracts;
- consistency requirements;
- migration dependencies;
- operational and compliance constraints;
- acceptance and rollback criteria.

## Incremental extraction

Prefer a reversible sequence:

1. characterize current behavior;
2. introduce an observable boundary;
3. route a controlled slice through the new implementation;
4. compare old and new outcomes;
5. migrate ownership and data deliberately;
6. remove old paths only after acceptance criteria pass.

Shared databases and dual writes are migration risks, not permanent target
architecture assumptions.

## Database split strategy

Define data ownership from evidenced business responsibility before selecting a
physical split. Evaluate:

- current tables, schemas, transactions, reporting, and consumers;
- authoritative owner for each data set;
- cross-context consistency and query requirements;
- historical data, retention, audit, and compliance constraints;
- migration, reconciliation, rollback, and coexistence needs.

Present applicable options and trade-offs:

- shared database with ownership rules as a temporary transition;
- schema-per-context before physical database separation;
- database-per-service with APIs or events;
- replicated read models for cross-context queries;
- change-data capture or outbox for controlled propagation;
- staged backfill followed by ownership cutover.

Do not recommend splitting tables only because services are split. Do not retain a
shared database as a permanent target without explicit approval.
