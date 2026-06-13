# Operation 03 - Domains and Capabilities

## Discover Business Language

Extract nouns, verbs, states, decisions, outcomes, and actor names from:

- domain and application code;
- UI labels, forms, menus, and error messages;
- tests and fixtures;
- APIs, events, schemas, reports, and documentation.

Create a glossary and flag ambiguous or overloaded terms.

## Extract Domain Models

Identify:

- entities and identities;
- value objects and constraints;
- aggregate and transaction-boundary candidates;
- state machines and lifecycle owners;
- policies, calculations, and domain services;
- commands, events, and read models.

Distinguish observed implementation models from proposed domain interpretations.

## Map Capabilities

A capability describes what the business must be able to do, independent of the
current technical solution.

For each capability, document:

- `CAP-###` ID and name;
- business purpose and outcome;
- actors and triggers;
- processes and rules it contains;
- authoritative data and systems involved;
- upstream/downstream dependencies;
- maturity, pain points, confidence, and evidence.

Group capabilities into domains or bounded-context candidates using vocabulary,
decisions, data authority, lifecycle, reasons to change, and team ownership.

## Validate Boundaries

Reject boundaries based only on folders, tables, APIs, or deployables. Record
alternative interpretations and boundary gaps when evidence is insufficient.

