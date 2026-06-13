#!/usr/bin/env python3
"""Create a structural and git inventory for one or more codebases."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXCLUDES = {
    ".git", ".idea", ".vscode", "__pycache__", "bin", "build", "coverage",
    "dist", "node_modules", "obj", "target", "vendor",
}
MANIFESTS = {
    "angular.json", "build.gradle", "build.gradle.kts", "cargo.toml",
    "composer.json", "dockerfile", "gemfile", "go.mod", "package.json",
    "pom.xml", "pyproject.toml", "requirements.txt", "serverless.yml",
    "template.yaml",
}
DOC_NAMES = {
    "architecture.md", "contributing.md", "documentation.md", "readme.md",
}
TEST_MARKERS = {"test", "tests", "spec", "specs", "__tests__"}
ENTRY_STEMS = {"app", "application", "index", "main", "program", "server", "startup"}
SCHEMA_MARKERS = {"migration", "migrations", "schema", "schemas"}


def git(root: Path, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def infer_roles(paths: list[str]) -> list[str]:
    text = " ".join(paths).lower()
    roles: set[str] = set()
    signals = {
        "frontend": ("clientapp", "frontend", "/src/app/", "angular.json"),
        "api": ("controller", "resolver", "routes", "openapi", "swagger"),
        "worker": ("consumer", "listener", "lambda", "worker", "scheduler"),
        "data": ("migration", "repository", "schema", "storedprocedure", "context"),
        "infrastructure": (".tf", "dockerfile", ".github/workflows", "serverless"),
        "library": ("pkg/", "lib/", "shared/", "common/"),
    }
    for role, markers in signals.items():
        if any(marker in text for marker in markers):
            roles.add(role)
    return sorted(roles or {"unknown"})


def inspect(root: Path) -> dict[str, object]:
    extensions: Counter[str] = Counter()
    paths: list[str] = []
    manifests: list[str] = []
    docs: list[str] = []
    tests: list[str] = []
    entries: list[str] = []
    schemas: list[str] = []
    infrastructure: list[str] = []

    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(directory for directory in dirs if directory not in EXCLUDES)
        current_path = Path(current)
        for filename in sorted(files):
            path = current_path / filename
            relative = path.relative_to(root).as_posix()
            lowered = filename.lower()
            lowered_parts = {part.lower() for part in path.parts}
            paths.append(relative)
            extensions[path.suffix.lower() or "<no-extension>"] += 1
            if lowered in MANIFESTS:
                manifests.append(relative)
            if lowered in DOC_NAMES:
                docs.append(relative)
            if lowered_parts & TEST_MARKERS or ".test." in lowered or ".spec." in lowered or lowered.endswith("_test.go"):
                tests.append(relative)
            if path.stem.lower() in ENTRY_STEMS:
                entries.append(relative)
            if lowered_parts & SCHEMA_MARKERS or path.suffix.lower() == ".sql":
                schemas.append(relative)
            if path.suffix.lower() in {".tf", ".yaml", ".yml"} or lowered == "dockerfile":
                infrastructure.append(relative)

    return {
        "name": root.name,
        "path": str(root),
        "remote": git(root, "config", "--get", "remote.origin.url"),
        "branch": git(root, "branch", "--show-current"),
        "commit": git(root, "rev-parse", "HEAD"),
        "dirty": bool(git(root, "status", "--porcelain")),
        "total_files": len(paths),
        "extensions": dict(sorted(extensions.items())),
        "manifests": manifests,
        "documentation_candidates": docs,
        "entry_point_candidates": entries,
        "test_file_candidates": tests,
        "schema_candidates": schemas,
        "infrastructure_candidates": infrastructure,
        "inferred_roles": infer_roles(paths),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("codebases", nargs="+", help="repository or codebase paths")
    parser.add_argument("--analysis-name", required=True)
    parser.add_argument("--output", help="JSON output path; defaults to stdout")
    args = parser.parse_args()

    codebases = []
    missing = []
    for raw in args.codebases:
        root = Path(raw).expanduser().resolve()
        if root.is_dir():
            codebases.append(inspect(root))
        else:
            missing.append(str(root))

    result = {
        "schema_version": 1,
        "analysis_name": args.analysis_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "codebases": codebases,
        "missing_paths": missing,
    }
    payload = json.dumps(result, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

