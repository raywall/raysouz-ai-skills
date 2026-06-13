# Operation 05 - Integrations and Data

## Integration Map

For each `INT-###`, document:

- producer, consumer, direction, and purpose;
- protocol: API, event, queue, file, job, webhook, or shared store;
- contract shape and versioning;
- authentication and authorization;
- timeout, retry, ordering, idempotency, DLQ, fallback, and compensation;
- consistency expectation and failure impact;
- evidence, owner, and gaps.

Trace contracts across repositories whenever source is available. If only one
side is visible, mark the other side as inferred.

## Data Ownership

For each `DATA-###`, identify:

- business meaning and lifecycle;
- authoritative writer and consumers;
- storage and schema;
- constraints and transaction scope;
- read models, replication, caching, and reporting use;
- retention, audit, privacy, and compliance signals;
- shared ownership or ambiguity.

Shared database access is coupling evidence, not proof of shared domain
ownership.

## Diagrams

Generate:

- integration/context diagram;
- key journey sequence diagrams;
- authoritative-data and read-model flow;
- shared-store/coupling diagram when relevant.

