# Operation 02 - Structure and Landscape

## Analyze in Parallel

Analyze repositories independently first, then synthesize centrally.

For each repository, identify:

- deployables and runtime entry points;
- modules, layers, dependency direction, and architectural patterns;
- APIs, UI routes, commands, consumers, schedulers, and jobs;
- storage technologies and schema/migration locations;
- configuration, feature flags, authorization, and secret-management approach;
- tests, CI/CD, infrastructure, observability, and operational controls;
- outbound references to other systems.

## Build the Landscape

Create:

- repository/system responsibility table;
- current architecture Mermaid diagram;
- dependency and deployment map;
- coupling observations;
- implementation constraints and missing evidence.

Describe technical structure as current state. Do not infer business boundaries
from structure alone.

## Structural Risk Signals

Record evidence of:

- shared databases and cross-schema access;
- cyclic dependencies;
- distributed transactions or fragile orchestration;
- business logic in UI, SQL, scripts, or infrastructure;
- duplicated rules;
- hard-coded configuration and secrets;
- unowned integrations;
- missing tests or operational controls.

