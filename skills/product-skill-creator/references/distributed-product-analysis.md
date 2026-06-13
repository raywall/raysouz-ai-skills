# Distributed Product Analysis

## Product Boundary

A product boundary follows customer or operational outcomes. It can include
multiple deployables and repositories. A repository can also serve several
products.

## Boundary Signals

Strong domain signals:

- distinct business decisions and invariants;
- authoritative lifecycle and data ownership;
- unique vocabulary;
- independent reasons to change;
- explicit team ownership;
- stable contracts with other capabilities.

Weak signals:

- folder structure;
- controller grouping;
- framework layers;
- deployment units;
- database tables alone.

## Trace Across Boundaries

At each API, event, file, or shared-store boundary, capture:

- producer and consumer;
- trigger and direction;
- request/event schema;
- correlation and idempotency behavior;
- retries, timeout, DLQ, fallback, or compensation;
- consistency expectation;
- owner of the contract and data.

## Shared Database

Treat a shared database as integration evidence and coupling, not shared domain
ownership. Identify writers, readers, transaction scope, joins, and hidden
dependencies.

## Frontend Behavior

Inspect frontend code for workflow, validation, calculations, feature flags, and
authorization. Product behavior implemented only in a frontend remains product
behavior, but record the trust and consistency risk.

## Reports and Read Models

Reports often reveal product vocabulary, important outcomes, and cross-domain
dependencies. Do not make reporting queries the authority for transactional
rules.

