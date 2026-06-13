#!/usr/bin/env python3
"""Report likely sensitive values in generated text artifacts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = {
    "email-address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "secret-assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|client[_-]?secret|password|passwd|token)\b\s*[:=]\s*[\"']?[^<\s\"']{6,}"
    ),
    "bearer-token": re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    "aws-access-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "private-ipv4": re.compile(
        r"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.(?:\d{1,3}\.)\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})\b"
    ),
    "internal-url": re.compile(
        r"(?i)\bhttps?://[^\s<>\"]+\.(?:internal|intranet|corp|local)(?:[/:][^\s<>\"]*)?"
    ),
}

TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".rst",
    ".txt",
    ".yaml",
    ".yml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan generated text artifacts for likely sensitive values."
    )
    parser.add_argument("paths", nargs="+", help="files or directories to scan")
    return parser.parse_args()


def files_under(paths: list[str]):
    for raw in paths:
        path = Path(raw)
        if path.is_file():
            yield path
        elif path.is_dir():
            for candidate in sorted(path.rglob("*")):
                if candidate.is_file() and candidate.suffix.lower() in TEXT_SUFFIXES:
                    yield candidate


def main() -> int:
    args = parse_args()
    findings = 0
    for path in files_under(args.paths):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(lines, start=1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings += 1
                    print(f"{path}:{line_number}: {name}")

    if findings:
        print(f"REVIEW REQUIRED: {findings} potential sensitive value(s) found")
        return 1
    print("No potential sensitive values found by automated scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
