#!/usr/bin/env python3
"""Initialize a software-factory workspace."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


DIRECTORIES = [
    "10-functional",
    "20-domain",
    "30-services",
    "40-generated",
    "50-simulations",
    "60-workflows",
    "90-decisions",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    analysis = Path(args.analysis).expanduser().resolve()
    if not analysis.is_dir():
        parser.error(f"analysis directory not found: {analysis}")

    root = Path(args.output).expanduser().resolve() / "_software-factory"
    root.mkdir(parents=True, exist_ok=True)
    for directory in DIRECTORIES:
        (root / directory).mkdir(exist_ok=True)

    manifest = {
        "schema_version": "1.0",
        "project_name": args.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_analysis": str(analysis),
        "scope": {"capabilities": [], "journeys": [], "rules": []},
        "targets": [],
        "stages": {
            "functional": "pending",
            "domain": "pending",
            "services": "pending",
            "generated": "pending",
            "simulation": "pending",
            "workflow": "pending",
        },
        "decisions": [],
        "gaps": [],
    }
    manifest_path = root / "factory-manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
