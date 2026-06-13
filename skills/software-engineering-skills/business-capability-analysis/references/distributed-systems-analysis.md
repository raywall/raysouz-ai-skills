# Distributed Systems Analysis

## Trace Across Boundaries

At each API, event, queue, file, job, or shared-store boundary, record:

- producer and consumer;
- business purpose;
- contract and transformation;
- ownership and versioning;
- authentication and authorization;
- timeout, retry, ordering, idempotency, and duplicate handling;
- failure, DLQ, fallback, and compensation;
- consistency and user-visible outcome.

## Repository Discovery

Discover candidate repositories from outbound calls, deployment names, event
topics, module imports, and shared schemas. Include them only when approved and
accessible. Mark consumer-only observations as inferred.

## Common Risks

- synchronous chains with cascading failure;
- events without schema/version ownership;
- retries without idempotency;
- shared database writes;
- implicit contracts in duplicated DTOs;
- orchestration hidden across consumers;
- no terminal status visible to users;
- unbounded batch or fan-out behavior.

## Data Authority

Separate:

- authoritative writer;
- read consumer;
- replicated/read model;
- reporting copy;
- cache;
- shared store with unclear ownership.

