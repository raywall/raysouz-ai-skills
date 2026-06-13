#!/usr/bin/env python3
"""Validate that required approvals exist before a decomposition phase."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIREMENTS = {
    "analysis": [
        "scope_confirmed",
        "approved_sources_confirmed",
        "clarifications_confirmed",
    ],
    "decomposition": [
        "scope_confirmed",
        "approved_sources_confirmed",
        "clarifications_confirmed",
        "current_state_confirmed",
    ],
    "proposal": [
        "scope_confirmed",
        "approved_sources_confirmed",
        "clarifications_confirmed",
        "current_state_confirmed",
        "sensitive_data_reviewed",
    ],
    "implementation": [
        "scope_confirmed",
        "approved_sources_confirmed",
        "clarifications_confirmed",
        "current_state_confirmed",
        "boundaries_approved",
        "target_stack_approved",
    ],
    "publish": [
        "scope_confirmed",
        "approved_sources_confirmed",
        "clarifications_confirmed",
        "current_state_confirmed",
        "boundaries_approved",
        "target_stack_approved",
        "sensitive_data_reviewed",
    ],
}

VALID_MODES = {"propose", "operate"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate decomposition phase readiness.")
    parser.add_argument("state", help="JSON state file based on templates/decomposition-state.json")
    parser.add_argument("--phase", choices=REQUIREMENTS, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.state)
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid state JSON: {exc}")
        return 2

    failures = [
        field for field in REQUIREMENTS[args.phase] if state.get(field) is not True
    ]
    mode = state.get("mode")
    if mode not in VALID_MODES:
        failures.append("mode must be propose or operate")
    elif args.phase == "proposal" and mode != "propose":
        failures.append(f"mode={mode} cannot enter proposal phase")
    elif args.phase in {"implementation", "publish"} and mode != "operate":
        failures.append(f"mode={mode} cannot enter {args.phase} phase")
    gaps = state.get("open_blocking_gaps", [])
    if not isinstance(gaps, list):
        print("ERROR: open_blocking_gaps must be a JSON array")
        return 2
    if gaps:
        failures.append(f"open_blocking_gaps={','.join(map(str, gaps))}")

    if failures:
        print(f"BLOCKED: {args.phase} phase is not ready")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"READY: {args.phase} phase requirements are satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
