#!/usr/bin/env python3
"""Validate the structure and minimum content of a generated product skill."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_REFERENCES = {
    "product-overview.md",
    "domains-and-contexts.md",
    "processes-and-journeys.md",
    "functional-requirements.md",
    "business-rules.md",
    "system-landscape.md",
    "data-and-integrations.md",
    "glossary.md",
    "gaps-and-decisions.md",
}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version", "product", "skill_name", "generated_at", "repositories", "counts",
}


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill_file = root / "SKILL.md"
    manifest_file = root / "product-manifest.json"
    references = root / "references"

    if not skill_file.is_file():
        errors.append("SKILL.md not found")
    else:
        content = skill_file.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            errors.append("SKILL.md has invalid YAML frontmatter")
        else:
            frontmatter = match.group(1)
            name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
            desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
            if not name_match:
                errors.append("SKILL.md frontmatter is missing name")
            elif name_match.group(1).strip() != root.name:
                errors.append("SKILL.md name must match directory name")
            if not desc_match or len(desc_match.group(1).strip()) < 80:
                errors.append("SKILL.md description must explain product usage and triggers")
        for reference in REQUIRED_REFERENCES:
            if f"references/{reference}" not in content:
                errors.append(f"SKILL.md does not reference references/{reference}")

    if not manifest_file.is_file():
        errors.append("product-manifest.json not found")
    else:
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            missing = REQUIRED_MANIFEST_FIELDS - set(manifest)
            if missing:
                errors.append(f"manifest missing fields: {', '.join(sorted(missing))}")
            if manifest.get("skill_name") != root.name:
                errors.append("manifest skill_name must match directory name")
            if not isinstance(manifest.get("repositories"), list):
                errors.append("manifest repositories must be a list")
        except json.JSONDecodeError as error:
            errors.append(f"invalid product-manifest.json: {error}")

    if not references.is_dir():
        errors.append("references directory not found")
    else:
        present = {path.name for path in references.iterdir() if path.is_file()}
        for missing in sorted(REQUIRED_REFERENCES - present):
            errors.append(f"missing reference: references/{missing}")
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in references.iterdir() if path.is_file()
        )
        if not re.search(r"\b(?:EVD|GAP|BR|FR|JRN|DOM)-\d{3}\b", combined):
            errors.append("references contain no stable evidence, gap, rule, requirement, journey, or domain IDs")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_product_skill.py <product-skill-directory>")
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Product skill is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

