#!/usr/bin/env python3
"""Create a structural and git inventory for one or more product repositories."""

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
    "composer.json", "dockerfile", "go.mod", "package.json", "pom.xml",
    "pyproject.toml", "requirements.txt", "serverless.yml", "template.yaml",
}
DOC_NAMES = {"readme.md", "documentation.md", "contributing.md", "architecture.md"}
INFRA_SUFFIXES = {".tf", ".yaml", ".yml"}
TEST_MARKERS = {"test", "tests", "spec", "specs", "__tests__"}


def run_git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def infer_roles(manifests: list[str], extensions: Counter[str], paths: list[str]) -> list[str]:
    text = " ".join(paths).lower()
    roles: set[str] = set()
    if any(token in text for token in ("clientapp", "/src/app/", "frontend", "angular.json")):
        roles.add("frontend")
    if any(token in text for token in ("controller", "routes", "handler", "api")):
        roles.add("api")
    if any(token in text for token in ("worker", "consumer", "listener", "function", "lambda")):
        roles.add("worker")
    if any(token in text for token in ("migration", "schema", "database", "repository", "context")):
        roles.add("data")
    if any(path.endswith((".tf", ".yaml", ".yml")) for path in paths):
        roles.add("infrastructure")
    if not roles and manifests:
        roles.add("application")
    return sorted(roles or {"unknown"})


def inspect_repository(root: Path) -> dict[str, object]:
    extensions: Counter[str] = Counter()
    manifests: list[str] = []
    docs: list[str] = []
    tests: list[str] = []
    infra: list[str] = []
    paths: list[str] = []
    total_files = 0

    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(directory for directory in dirs if directory not in EXCLUDES)
        current_path = Path(current)
        for filename in sorted(files):
            path = current_path / filename
            relative = path.relative_to(root).as_posix()
            lowered = filename.lower()
            parts = {part.lower() for part in path.parts}
            total_files += 1
            paths.append(relative)
            extensions[path.suffix.lower() or "<no-extension>"] += 1
            if lowered in MANIFESTS:
                manifests.append(relative)
            if lowered in DOC_NAMES:
                docs.append(relative)
            if parts & TEST_MARKERS or ".test." in lowered or ".spec." in lowered or lowered.endswith("_test.go"):
                tests.append(relative)
            if path.suffix.lower() in INFRA_SUFFIXES or lowered == "dockerfile":
                infra.append(relative)

    remote = run_git(root, "config", "--get", "remote.origin.url")
    branch = run_git(root, "branch", "--show-current")
    commit = run_git(root, "rev-parse", "HEAD")
    dirty_output = run_git(root, "status", "--porcelain")

    return {
        "name": root.name,
        "path": str(root),
        "remote": remote,
        "branch": branch,
        "commit": commit,
        "dirty": bool(dirty_output),
        "total_files": total_files,
        "extensions": dict(sorted(extensions.items())),
        "manifests": manifests,
        "documentation_candidates": docs,
        "test_file_candidates": tests,
        "infrastructure_candidates": infra,
        "inferred_roles": infer_roles(manifests, extensions, paths),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repositories", nargs="+", help="repository directories")
    parser.add_argument("--product", required=True, help="product name")
    parser.add_argument("--output", help="output JSON path; defaults to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repositories = []
    missing = []
    for raw in args.repositories:
        root = Path(raw).expanduser().resolve()
        if root.is_dir():
            repositories.append(inspect_repository(root))
        else:
            missing.append(str(root))

    result = {
        "schema_version": 1,
        "product": args.product,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repositories": repositories,
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

