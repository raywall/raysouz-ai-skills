#!/usr/bin/env python3
"""Validate business capability analysis artifact structure and traceability."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED = {
    "analysis-manifest.json", "evidence-register.md", "executive-summary.md",
    "system-structure.md", "domain-model.md", "capability-map.md",
    "business-processes.md", "business-rules.md", "integrations-and-data.md",
    "risks-and-opportunities.md", "gaps-and-decisions.md",
    "traceability-matrix.md",
}
MANIFEST_FIELDS = {
    "schema_version", "analysis_name", "mode", "generated_at", "repositories",
    "coverage",
}
ID_PATTERNS = {
    "evidence or explicit evidence gap": r"\b(?:EVD|GAP)-\d{3}\b",
    "capability or explicit capability gap": r"\b(?:CAP|GAP)-\d{3}\b",
    "journey or explicit journey gap": r"\b(?:JRN|GAP)-\d{3}\b",
    "gap": r"\bGAP-\d{3}\b",
}


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for filename in sorted(REQUIRED):
        if not (root / filename).is_file():
            errors.append(f"missing artifact: {filename}")

    manifest_path = root / "analysis-manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            missing = MANIFEST_FIELDS - set(manifest)
            if missing:
                errors.append(f"manifest missing fields: {', '.join(sorted(missing))}")
            if not isinstance(manifest.get("repositories"), list):
                errors.append("manifest repositories must be a list")
            if not isinstance(manifest.get("coverage"), dict):
                errors.append("manifest coverage must be an object")
        except json.JSONDecodeError as error:
            errors.append(f"invalid analysis-manifest.json: {error}")

    content = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in root.glob("*.md")
    )
    for name, pattern in ID_PATTERNS.items():
        if not re.search(pattern, content):
            errors.append(f"no {name} IDs found")

    if not re.search(r"\b(?:BR-(?:VAL|CALC|DEC|STATE)-\d{3}|GAP-\d{3})\b", content):
        errors.append("no business rule IDs or explicit business-rule gap found")
    if not re.search(r"\b(?:INT-\d{3}|GAP-\d{3})\b", content):
        errors.append("no integration IDs or explicit integration gap found")
    if not re.search(r"\b(?:OPP-\d{3}|GAP-\d{3})\b", content):
        errors.append("no opportunity IDs or explicit opportunity gap found")
    if not re.search(r"\b(?:DOM-\d{3}|GAP-\d{3})\b", content):
        errors.append("no domain IDs or explicit domain gap found")
    if not re.search(r"\b(?:DATA-\d{3}|GAP-\d{3})\b", content):
        errors.append("no data IDs or explicit data gap found")
    if not re.search(r"\b(?:RISK-\d{3}|GAP-\d{3})\b", content):
        errors.append("no risk IDs or explicit risk gap found")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis_directory")
    args = parser.parse_args()
    errors = validate(Path(args.analysis_directory).expanduser().resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Analysis structure is valid; unresolved gaps may remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
