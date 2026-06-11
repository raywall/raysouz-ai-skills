#!/usr/bin/env python3
"""Create a content-free structural inventory of a codebase."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

DEFAULT_EXCLUDES = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

MANIFESTS = {
    "build.gradle",
    "build.gradle.kts",
    "cargo.toml",
    "composer.json",
    "dockerfile",
    "gemfile",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
}

ENTRY_NAMES = {
    "app",
    "application",
    "index",
    "main",
    "program",
    "server",
}

TEST_MARKERS = {"test", "tests", "spec", "specs", "__tests__"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a language-agnostic structural inventory without reading file contents."
    )
    parser.add_argument("root", help="codebase root")
    parser.add_argument("--output", help="write JSON to this path instead of stdout")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="additional directory name to exclude; repeat as needed",
    )
    return parser.parse_args()


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def inventory(root: Path, excludes: set[str]) -> dict[str, object]:
    extensions: Counter[str] = Counter()
    manifests: list[str] = []
    test_files: list[str] = []
    entry_candidates: list[str] = []
    directories: set[str] = set()
    total_files = 0

    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in excludes)
        current_path = Path(current)
        if current_path != root:
            directories.add(relative(root, current_path))

        for filename in sorted(filenames):
            path = current_path / filename
            total_files += 1
            suffix = path.suffix.lower() or "<no-extension>"
            extensions[suffix] += 1

            lowered = filename.lower()
            rel = relative(root, path)
            parts = {part.lower() for part in path.parts}
            stem = path.stem.lower()

            if lowered in MANIFESTS:
                manifests.append(rel)
            if parts & TEST_MARKERS or ".test." in lowered or ".spec." in lowered:
                test_files.append(rel)
            if stem in ENTRY_NAMES:
                entry_candidates.append(rel)

    return {
        "root": str(root),
        "inventory_kind": "structural-only",
        "total_files": total_files,
        "total_directories": len(directories),
        "extensions": dict(sorted(extensions.items())),
        "manifests": manifests,
        "entry_point_candidates": entry_candidates,
        "test_file_candidates": test_files,
        "excluded_directory_names": sorted(excludes),
    }


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"error: codebase root is not a directory: {root}")

    result = inventory(root, DEFAULT_EXCLUDES | set(args.exclude))
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
