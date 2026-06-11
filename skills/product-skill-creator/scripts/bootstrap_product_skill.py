#!/usr/bin/env python3
"""Bootstrap a generated product skill from bundled templates."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not result:
        raise ValueError("product name cannot be converted to a skill name")
    return result[:63].rstrip("-")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True, help="product display name")
    parser.add_argument("--name", help="generated skill name; defaults from product")
    parser.add_argument("--output", required=True, help="parent output directory")
    parser.add_argument("--inventory", help="optional inventory JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_name = args.name or slug(args.product)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_name):
        raise SystemExit("error: skill name must use lowercase letters, digits, and hyphens")

    script_dir = Path(__file__).resolve().parent
    templates = script_dir.parent / "templates"
    destination = Path(args.output).expanduser().resolve() / skill_name
    if destination.exists():
        raise SystemExit(f"error: destination already exists: {destination}")

    destination.mkdir(parents=True)
    skill_template = (templates / "generated-product-skill.md").read_text(encoding="utf-8")
    skill_content = (
        skill_template
        .replace("<product-skill-name>", skill_name)
        .replace("<Product>", args.product)
        .replace("<product>", args.product)
        .replace("<domains/journeys>", "its identified domains and journeys")
        .replace("<summary>", "GAP: complete from repository evidence")
        .replace("<outcomes>", "GAP: complete from repository evidence")
        .replace("<domains>", "GAP: complete from repository evidence")
        .replace("<repositories>", "GAP: complete from repository evidence")
        .replace("<timestamp>", datetime.now(timezone.utc).isoformat())
    )
    (destination / "SKILL.md").write_text(skill_content, encoding="utf-8")
    shutil.copytree(templates / "generated-references", destination / "references")

    inventory = {}
    if args.inventory:
        inventory = json.loads(Path(args.inventory).expanduser().read_text(encoding="utf-8"))
    manifest = {
        "schema_version": 1,
        "product": args.product,
        "skill_name": skill_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "last_verified": None,
        "analysis_scope": "GAP: complete after analysis",
        "excluded_systems": [],
        "repositories": inventory.get("repositories", []),
        "counts": {
            "domains": 0, "journeys": 0, "functional_requirements": 0,
            "business_rules": 0, "evidence": 0, "gaps": 1,
        },
    }
    (destination / "product-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
