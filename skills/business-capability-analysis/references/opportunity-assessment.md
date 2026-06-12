# Opportunity Assessment

## Assessment Dimensions

Evaluate each capability and journey across:

- business value and pain;
- rule clarity and consistency;
- ownership and coupling;
- data authority and integrity;
- reliability and recoverability;
- security, privacy, and compliance;
- testability and observability;
- performance, scalability, and cost;
- change frequency and delivery friction.

## Opportunity Scoring

Rate:

- impact: high, medium, low;
- effort: high, medium, low;
- confidence: high, medium, low;
- reversibility: easy, moderate, difficult;
- dependencies: IDs of prerequisite opportunities or gaps.

Use scores for prioritization, not false numerical precision.

## Decomposition Candidate Signals

Strong signals:

- cohesive capabilities and language;
- distinct authoritative data and lifecycle;
- independent reasons to change;
- clear contracts;
- operational or scaling need;
- team ownership.

Warning signals:

- distributed invariant requires strong consistency;
- shared database and unclear owner;
- capability boundaries depend on missing systems;
- service would be CRUD-only or too small;
- extraction adds more operational cost than value.

## Rearcitecture Signals

Recommend rearchitecture only when evidence shows current constraints such as:

- reliability or scaling limits;
- excessive change coupling;
- inability to test or observe business outcomes;
- platform end-of-life or security risk;
- cost disproportionate to workload;
- repeated delivery pain.

Keep target-state choices proposed until constraints and acceptance criteria are
approved.

