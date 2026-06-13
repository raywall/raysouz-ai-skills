#!/usr/bin/env python3
"""Create the analysis artifact structure with explicit initial gaps."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ARTIFACTS = {
    "evidence-register.md": """# Evidence Register

| ID | Repository | Source | Type | Observation | Supports | Commit |
|---|---|---|---|---|---|---|

## Contradictions

| ID | Contradiction | Evidence | Impact | Required owner |
|---|---|---|---|---|
| GAP-001 | Analysis has not yet been completed | Inventory only | Business behavior is unknown | Analysis owner |
""",
    "executive-summary.md": """# Executive Summary

## Business Purpose

GAP-001: Complete from evidence.

## Central Capabilities and Domains

## Main Findings

## High-Impact Risks and Opportunities
""",
    "system-structure.md": """# System Structure

## Repository and System Responsibilities

## Current Architecture

## Structural Constraints and Coupling
""",
    "domain-model.md": """# Domain Model

## Glossary

## Entities, Value Objects, and Lifecycles

## Domain and Bounded-Context Candidates
""",
    "capability-map.md": """# Capability Map

| ID | Capability | Purpose/outcome | Systems | Maturity | Evidence/gaps |
|---|---|---|---|---|---|
""",
    "business-processes.md": """# Business Processes and Journeys

## Journey Index

## End-to-End Traces
""",
    "business-rules.md": """# Business Logic and Rules

## Validations

## Calculations

## Decisions

## State Transitions

## Edge Cases and Error States
""",
    "integrations-and-data.md": """# Integrations and Data

## Integration Map

## Contracts and Failure Handling

## Data Authority and Ownership
""",
    "risks-and-opportunities.md": """# Risks and Opportunities

## Risks

## Opportunities
""",
    "gaps-and-decisions.md": """# Gaps and Decisions

| ID | Gap or decision | Impact | Required source/owner | Status |
|---|---|---|---|---|
| GAP-001 | Complete current-state analysis | Business behavior is unknown | Analysis owner | Open |
""",
    "traceability-matrix.md": """# Traceability Matrix

| Capability | Domain | Journeys | Rules | Data | Systems | Evidence | Opportunities |
|---|---|---|---|---|---|---|---|
""",
}


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return result or "analysis"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--inventory")
    parser.add_argument("--mode", default="landscape", choices=["landscape", "focused", "refresh", "assessment"])
    args = parser.parse_args()

    root = Path(args.output).expanduser().resolve() / "_business-capability-analysis"
    if root.exists():
        raise SystemExit(f"error: analysis directory already exists: {root}")
    root.mkdir(parents=True)

    inventory = {}
    if args.inventory:
        inventory = json.loads(Path(args.inventory).expanduser().read_text(encoding="utf-8"))
    manifest = {
        "schema_version": 1,
        "analysis_name": args.name,
        "analysis_id": slug(args.name),
        "mode": args.mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "last_verified": None,
        "scope": "GAP-001: complete after analysis",
        "excluded_systems": inventory.get("missing_paths", []),
        "repositories": inventory.get("codebases", []),
        "coverage": {
            "systems": len(inventory.get("codebases", [])),
            "domains": 0, "capabilities": 0, "journeys": 0,
            "business_rules": 0, "integrations": 0, "data_sets": 0,
            "risks": 0, "opportunities": 0, "gaps": 1, "evidence": 0,
        },
    }
    (root / "analysis-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    for filename, content in ARTIFACTS.items():
        (root / filename).write_text(content, encoding="utf-8")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

