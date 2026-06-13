# Operation 02 - Product and Domain Discovery

## Product Discovery

Infer the product from behavior and user outcomes, not repository names.

Collect:

- actors and external systems;
- problems solved and outcomes delivered;
- entry triggers and terminal outcomes;
- capabilities exposed by UI, APIs, events, jobs, and reports;
- compliance, authorization, timing, and operational constraints.

Confirm important product claims with multiple evidence types when possible.

## Domain Discovery

Cluster capabilities using:

- distinct business language;
- business decisions and invariants;
- data authority and lifecycle;
- reasons to change;
- actors and outcomes;
- transactional and consistency boundaries;
- team ownership when evidenced.

Repositories, deployables, namespaces, and database tables are signals only.

For each proposed domain or bounded context, document:

- purpose and product outcome;
- classification: core, supporting, generic, or unknown;
- vocabulary;
- owned decisions and authoritative data;
- upstream/downstream dependencies;
- repositories that implement parts of it;
- confidence and evidence;
- unresolved boundary questions.

## Cross-Repository Context Map

Draw a Mermaid context map showing synchronous APIs, asynchronous events, shared
stores, and third parties. Explicitly mark shared database coupling and unclear
ownership.

Do not propose decomposition unless requested. The generated product skill
documents the current product and may include improvement opportunities as
`PROPOSED`, never as current fact.

