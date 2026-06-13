# Operation 06 - Risks and Opportunities

Assess only after the current-state model is sufficiently evidenced.

## Risks

Create `RISK-###` entries for material business and technical risks:

- rule inconsistency or business behavior in untrusted layers;
- unclear ownership or shared data;
- reliability and failure-recovery gaps;
- security, privacy, compliance, and audit issues;
- scalability, performance, and cost constraints;
- test, observability, maintainability, and operability gaps;
- high-coupling or high-change hotspots.

Include affected capabilities, journeys, evidence, likelihood, impact, and
current mitigations.

## Opportunities

Create `OPP-###` entries. Classify each as:

- process improvement or automation;
- domain/rule clarification;
- reliability, security, observability, testing, performance, or FinOps;
- modularization and ownership clarification;
- monolith decomposition candidate;
- rearchitecture or platform modernization candidate.

For every opportunity include:

- problem and evidence;
- expected business/technical value;
- affected capabilities, journeys, systems, and data;
- prerequisites and dependencies;
- risk and reversibility;
- validation needed;
- impact/effort/confidence rating.

## Guardrails

- Do not recommend microservices merely because modules exist.
- Do not recommend technology replacement without a measured constraint.
- Prefer reversible, incremental improvements.
- Mark target-state ideas as `PROPOSED`.

