# Evidence and Knowledge Policy

## Allowed evidence

Use only sources that the user confirms are approved corporate knowledge sources:

- source code, tests, configuration, schemas, and version history in authorized repositories;
- approved corporate documentation, catalogs, wikis, tickets, and architecture records;
- approved database schemas, data dictionaries, and sanitized query results;
- statements from identified domain experts supplied during the engagement.

Do not use public-domain assumptions or generic industry definitions to fill a
business gap. General engineering knowledge may guide investigation and
implementation technique, but it must not become an asserted business rule.

## Evidence register

Every material business statement must have an evidence ID. Record:

- source type and approved location;
- precise locator such as file and line, document section, ticket, or query ID;
- sanitized summary of what the source establishes;
- affected domain concept or decision;
- access and sensitivity notes;
- validation status and validating owner.

Use `templates/evidence-register.md`. Evidence locators belong in working
artifacts; generated public-facing documentation should contain only locators
approved for that audience.

## Fact, gap, and proposal

Classify findings without inventing missing information:

- **Established fact:** directly supported by registered evidence.
- **Open gap:** required information is absent, contradictory, or inaccessible.
- **Design proposal:** a suggested technical or decomposition choice, clearly
  separated from current business behavior and awaiting approval.

Never present a gap or proposal as an established fact.

## Mandatory clarification gate

Before decomposition begins, ask about every unresolved item that can change:

- business scope or migration objective;
- authoritative sources and their access;
- domain vocabulary or conflicting definitions;
- requested decomposition axis, such as segment, capability, geography, or team;
- ownership, compliance, data, availability, or deployment constraints;
- acceptance criteria and permitted target technologies.

Do not create target service boundaries or implementation code until blocking
gaps are answered or the user explicitly records a decision to defer them.

## Corporate database use

- Query only approved sources with least privilege.
- Prefer schemas, data dictionaries, and sanitized aggregates over production rows.
- Never copy personal data, credentials, tokens, account identifiers, or restricted
  URLs into skill outputs.
- Record the query or source identifier, not sensitive result values.
- Stop and ask for a sanitized source when evidence cannot be safely handled.
