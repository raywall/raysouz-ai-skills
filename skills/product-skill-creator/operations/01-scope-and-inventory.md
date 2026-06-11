# Operation 01 - Scope and Inventory

## Intake

Determine:

- mode: `create`, `refresh`, or `audit`;
- product name and desired generated skill name/path;
- starting repositories and approved additional sources;
- whether repositories represent the whole product or only a slice;
- target usage: analysis, implementation, review, testing, improvement, or all;
- known business owners, vocabulary, constraints, and high-risk journeys.

Ask only questions that cannot be answered from local evidence and would change
the analysis materially.

## Inventory

Run `scripts/inventory_repositories.py`. For each repository, record:

- canonical path, git remote, branch, commit, and dirty state;
- languages, manifests, likely entry points, tests, docs, IaC, schemas, and APIs;
- likely role: frontend, API, worker, library, infrastructure, data, or unknown.

Then inspect repository-level documentation and manifests. Do not deeply analyze
all source files yet.

## Discovery Boundary

Discover possible missing repositories from:

- HTTP/gRPC clients and server routes;
- event topics, queues, schemas, and consumers;
- package/module imports;
- shared databases and schemas;
- CI/CD deployment names and infrastructure references.

Record missing systems as gaps. Include additional repositories only when they
are locally available and approved.

## Outputs

- repository inventory;
- scope statement;
- approved evidence sources;
- missing-system register;
- initial product hypothesis clearly marked `INFERRED`.

