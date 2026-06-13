# Operation 07 - Synthesis and Validation

## Synthesize

Complete all artifacts from `templates/output-catalog.md`. Keep current-state
facts separate from inferences, gaps, and proposed opportunities.

The executive summary must answer:

- what business outcomes the solution enables;
- which capabilities and domains are central;
- how the main journeys work;
- where rules and data authority live;
- which integrations and constraints matter;
- the most important risks and opportunities.

## Traceability

Create links:

- capabilities to domains, journeys, rules, data, and systems;
- journeys to rules, integrations, errors, and evidence;
- opportunities to risks, capabilities, evidence, and prerequisites.

## Validate

Run:

```bash
python3 scripts/validate_analysis.py <analysis-directory>
python3 scripts/scan_artifacts.py <analysis-directory>
```

Then manually sample:

- at least three rules against source evidence;
- at least two end-to-end journeys;
- at least two integration contracts;
- all high-impact opportunities.

Report coverage, excluded systems, contradictions, gaps requiring business-owner
validation, and validation results.

