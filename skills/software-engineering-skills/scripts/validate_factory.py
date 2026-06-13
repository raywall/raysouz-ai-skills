#!/usr/bin/env python3
"""Validate software-factory handoff artifacts using only the standard library."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FIXED_STAGES = {
    "functional": (
        "10-functional",
        [
            "functional-specification.md",
            "acceptance-scenarios.md",
            "data-contracts.md",
            "traceability-matrix.md",
        ],
    ),
    "domain": (
        "20-domain",
        [
            "domain-landscape.md",
            "context-map.md",
            "model-catalog.md",
            "service-catalog.md",
            "traceability-matrix.md",
        ],
    ),
}

PATTERN_STAGES = {
    "services": [
        "30-services/*/service-blueprint.yaml",
        "30-services/*/acceptance-criteria.md",
        "30-services/*/traceability.md",
    ],
    "generated": ["40-generated/*/generation-report.md"],
    "simulation": ["50-simulations/*/*.yaml", "50-simulations/*/scenario-matrix.md"],
    "workflow": ["60-workflows/*/config.yaml", "60-workflows/*/workflows/*.yaml"],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    parser.add_argument(
        "--stage",
        choices=["manifest", *FIXED_STAGES, *PATTERN_STAGES, "all"],
        default="all",
    )
    args = parser.parse_args()

    root = Path(args.workspace).expanduser().resolve()
    errors: list[str] = []
    manifest_path = root / "factory-manifest.json"
    if not manifest_path.is_file():
        errors.append("missing factory-manifest.json")
    else:
        try:
            manifest = json.loads(manifest_path.read_text())
            for field in ("schema_version", "project_name", "source_analysis", "stages"):
                if not manifest.get(field):
                    errors.append(f"manifest missing field: {field}")
        except json.JSONDecodeError as exc:
            errors.append(f"invalid factory-manifest.json: {exc}")

    if args.stage == "manifest":
        selected_fixed = {}
        selected_patterns = {}
    elif args.stage == "all":
        selected_fixed = FIXED_STAGES
        selected_patterns = PATTERN_STAGES
    else:
        selected_fixed = (
            {args.stage: FIXED_STAGES[args.stage]} if args.stage in FIXED_STAGES else {}
        )
        selected_patterns = (
            {args.stage: PATTERN_STAGES[args.stage]} if args.stage in PATTERN_STAGES else {}
        )

    for stage, (directory, files) in selected_fixed.items():
        for filename in files:
            path = root / directory / filename
            if not path.is_file() or not path.read_text().strip():
                errors.append(f"{stage}: missing or empty {path.relative_to(root)}")

    for stage, patterns in selected_patterns.items():
        for pattern in patterns:
            matches = [path for path in root.glob(pattern) if path.is_file()]
            if not matches:
                errors.append(f"{stage}: no artifacts match {pattern}")
                continue
            for path in matches:
                if not path.read_text().strip():
                    errors.append(f"{stage}: empty {path.relative_to(root)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("software-factory workspace is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
