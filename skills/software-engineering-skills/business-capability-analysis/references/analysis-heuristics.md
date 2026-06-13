# Analysis Heuristics

## Search Order

1. Inventory structure and manifests.
2. Identify entry points and boundaries.
3. Trace representative journeys.
4. Follow data and state transitions.
5. Extract rules and domain vocabulary.
6. Synthesize capabilities and domains.

Avoid exhaustive file-by-file reading before locating important journeys.

## Where Business Behavior Hides

- frontend forms, calculations, guards, and route visibility;
- controllers, handlers, use cases, services, and domain models;
- database constraints, triggers, procedures, and queries;
- consumers, schedulers, scripts, and batch jobs;
- configuration, feature flags, and policy files;
- tests, fixtures, user-facing messages, and reports.

## Pattern Signals

| Signal | Likely meaning | Caution |
|---|---|---|
| Entity/value object/aggregate | domain model candidate | may be an anemic DTO |
| Command/use case/handler | capability or action | may be purely technical |
| Domain event | important business occurrence | may be integration plumbing |
| State enum/transitions | lifecycle | verify all transition paths |
| Validation/error message | rule or requirement | may be UI-only |
| Report/query | outcome and vocabulary | not necessarily authority |
| Shared database join | hidden integration | not shared domain ownership |
| Feature flag/config branch | policy or rollout | distinguish business from operations |

## Evidence Discipline

Use `EVD-###` records containing repository, source path/symbol, observation,
commit, and supported IDs.

Confidence:

- `CONFIRMED`: directly evidenced and consistent;
- `INFERRED`: likely interpretation requiring validation;
- `GAP`: unknown, unavailable, or contradictory;
- `PROPOSED`: opportunity or target-state idea.

