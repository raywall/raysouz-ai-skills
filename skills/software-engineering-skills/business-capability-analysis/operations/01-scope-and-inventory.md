# Operation 01 - Scope and Inventory

## Establish Scope

Determine:

- analysis mode and objective;
- starting repositories, directories, or files;
- desired output location;
- business/product scope and exclusions;
- approved evidence sources;
- whether additional repositories may be included;
- known critical journeys, incidents, pain points, or modernization goals.

Ask only questions whose answers cannot be discovered and would materially alter
the analysis.

## Inventory

Run `scripts/inventory_codebases.py`. Record per repository:

- canonical path, remote, branch, commit, and dirty state;
- languages, manifests, entry points, tests, docs, schemas, IaC, and workflows;
- likely role: UI, API, worker, data, library, infrastructure, or unknown.

Read top-level documentation, manifests, deployment configuration, and solution
files. Do not deeply trace all code yet.

## Discover Missing Systems

Identify discovery targets from:

- outbound clients and inbound routes;
- events, topics, queues, jobs, and webhooks;
- shared packages and module references;
- database/schema references;
- infrastructure and deployment names.

Record unavailable systems as gaps. Do not clone or add repositories without
approval.

## Outputs

- analysis manifest;
- structural inventory;
- scope and exclusions;
- initial system landscape;
- missing-system and evidence-source gaps.

