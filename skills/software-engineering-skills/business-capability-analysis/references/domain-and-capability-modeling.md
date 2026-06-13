# Domain and Capability Modeling

## Domain Model

Extract business concepts and behavior:

- entity: identity and lifecycle;
- value object: immutable descriptive concept;
- aggregate candidate: consistency and transaction boundary;
- policy/domain service: decision spanning concepts;
- event: business-significant occurrence;
- state machine: allowed lifecycle transitions.

Do not force DDD terminology when evidence does not support it. Mark candidates
as inferred.

## Business Capability

A business capability states **what the business must be able to do**, not the
workflow or system used to do it.

Good capability names are stable verb-noun phrases:

- Manage customer eligibility
- Calculate settlement amount
- Approve claim
- Reconcile payment

Avoid names tied to current technology:

- Call payment API
- Process Kafka message
- Update orders table

## Capability Record

For each `CAP-###`, capture:

- purpose and business outcome;
- actors and triggers;
- included decisions and processes;
- authoritative data;
- dependencies and integrations;
- implementing repositories/systems;
- maturity, pain points, evidence, and confidence.

## Domain Boundaries

Cluster capabilities using:

- shared and distinct vocabulary;
- business decisions and invariants;
- lifecycle and authoritative data;
- reasons to change;
- consistency requirements;
- team ownership where evidenced.

Technical modules and deployables may support a boundary hypothesis but cannot
establish it alone.

