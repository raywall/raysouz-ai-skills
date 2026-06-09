#!/usr/bin/env python3
"""
validate_config_pipe.py — Validate an config_pipe.yaml file against company rules.

Usage:
    python validate_config_pipe.py <path/to/config_pipe.yaml> [--repo-root <dir>] [--json]

Exit codes:
    0  valid (no errors; warnings allowed)
    1  invalid (one or more errors)
    2  could not run (file missing, unparseable YAML, etc.)

HOW TO CUSTOMIZE
----------------
This validator is driven by the RULES section below. You change WHAT gets
checked by editing RULES — you should rarely need to touch the engine.

Each rule has a `severity`: "error" blocks (exit 1), "warning" advises (exit 0).
The real config_pipe schema is internal, so the rules here are a reasonable
placeholder. Replace field names/paths with the real ones as you learn them.
"""

from __future__ import annotations
import sys
import os
import argparse
import json

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml --break-system-packages", file=sys.stderr)
    sys.exit(2)


# ─────────────────────────────────────────────────────────────────────────────
# RULES — EDIT THIS SECTION to match your real config_pipe.yaml schema.
# ─────────────────────────────────────────────────────────────────────────────
#
# `required_fields`: dotted paths that must exist and be non-empty.
#   severity "error"  -> missing field fails validation
#   severity "warning"-> missing field warns only
#
# `path_fields`: dotted paths whose VALUE is a filesystem path that must exist
#   on disk (checked relative to --repo-root). Catches e.g. a build context or
#   terraform_dir pointing at a folder that isn't there.
#
# `enum_fields`: dotted paths whose value must be one of an allowed set.
#
# Cross-reference and structural checks that don't fit these tables live in
# `custom_checks()` further down.

REQUIRED_FIELDS = [
    ("application.name",            "error",   "Service must have a unique name."),
    ("application.owner",           "error",   "An owning team is required."),
    ("application.type",            "warning", "Workload type helps classify the service."),
    ("application.runtime",         "warning", "Runtime (language+version) should be declared."),
    ("build.context",              "error",   "Build context (application dir) is required."),
    ("build.dockerfile",           "warning", "Dockerfile path is usually expected."),
    ("infrastructure.terraform_dir","error",  "Pipeline must be linked to a Terraform dir."),
    ("pipeline.trigger",           "error",   "Pipeline needs a trigger."),
    ("pipeline.stages",            "error",   "Pipeline needs at least one stage."),
    ("environments",               "error",   "At least one environment must be defined."),
]

PATH_FIELDS = [
    ("build.context",               "error",   "Build context path does not exist."),
    ("build.dockerfile",            "warning", "Dockerfile not found at given path."),
    ("infrastructure.terraform_dir","error",   "Terraform dir does not exist."),
]

ENUM_FIELDS = [
    ("application.type", ["service", "worker", "cron", "library"], "warning"),
]

# Names of stages that, if present, must define an environment that exists.
DEPLOY_STAGE_NAMES = {"deploy", "release", "promote"}

# Environments considered "production" — deploys to these should require approval.
PROD_ENVIRONMENT_NAMES = {"prd", "prod", "production"}


# ─────────────────────────────────────────────────────────────────────────────
# Engine — generally no need to edit below this line.
# ─────────────────────────────────────────────────────────────────────────────

class Finding:
    def __init__(self, severity: str, code: str, message: str):
        self.severity = severity  # "error" | "warning"
        self.code = code
        self.message = message

    def to_dict(self):
        return {"severity": self.severity, "code": self.code, "message": self.message}


def get_path(data, dotted: str):
    """Return value at a dotted path, or a sentinel if absent."""
    MISSING = object()
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return MISSING
    return cur


MISSING = object()


def is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        return True
    return False


def check_required(data, findings):
    for path, severity, msg in REQUIRED_FIELDS:
        val = get_path(data, path)
        if val is get_path({}, "__never__") or _absent(data, path) or is_empty(val):
            findings.append(Finding(severity, "missing_field", f"`{path}` — {msg}"))


def _absent(data, dotted) -> bool:
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return True
    return False


def check_paths(data, findings, repo_root):
    for path, severity, msg in PATH_FIELDS:
        if _absent(data, path):
            continue  # absence handled by required-field check
        val = get_path(data, path)
        if not isinstance(val, str):
            continue
        full = os.path.join(repo_root, val)
        if not os.path.exists(full):
            findings.append(Finding(severity, "path_not_found",
                                    f"`{path}` = '{val}' — {msg}"))


def check_enums(data, findings):
    for path, allowed, severity in ENUM_FIELDS:
        if _absent(data, path):
            continue
        val = get_path(data, path)
        if val not in allowed:
            findings.append(Finding(severity, "bad_enum",
                f"`{path}` = '{val}' is not one of {allowed}."))


def custom_checks(data, findings):
    """Cross-reference and structural checks a flat schema can't express."""
    stages = get_path(data, "pipeline.stages")
    environments = get_path(data, "environments")
    env_names = set(environments.keys()) if isinstance(environments, dict) else set()

    if isinstance(stages, list):
        for i, stage in enumerate(stages):
            if not isinstance(stage, dict):
                findings.append(Finding("error", "bad_stage",
                    f"pipeline.stages[{i}] is not a mapping."))
                continue
            name = str(stage.get("name", f"<unnamed #{i}>"))

            # Deploy stages must target a defined environment.
            if name.lower() in DEPLOY_STAGE_NAMES or "environment" in stage:
                env = stage.get("environment")
                if not env:
                    findings.append(Finding("error", "deploy_no_env",
                        f"Stage '{name}' looks like a deploy but defines no `environment`."))
                elif env not in env_names:
                    findings.append(Finding("error", "undefined_env",
                        f"Stage '{name}' targets environment '{env}' "
                        f"not defined under `environments` ({sorted(env_names)})."))

                # Production deploys should require approval.
                if env in PROD_ENVIRONMENT_NAMES and not stage.get("requires_approval", False):
                    findings.append(Finding("warning", "prod_no_approval",
                        f"Stage '{name}' deploys to production '{env}' "
                        f"without `requires_approval: true`."))

            # No raw command at all is suspicious.
            if "run" not in stage and "uses" not in stage:
                findings.append(Finding("warning", "stage_no_action",
                    f"Stage '{name}' has neither `run` nor `uses`."))

    # Naive hardcoded-secret scan in environment variables.
    if isinstance(environments, dict):
        secretish = ("password", "secret", "token", "apikey", "api_key", "private_key")
        for env_name, env_cfg in environments.items():
            variables = (env_cfg or {}).get("variables", {}) if isinstance(env_cfg, dict) else {}
            if isinstance(variables, dict):
                for k, v in variables.items():
                    if any(s in k.lower() for s in secretish) and isinstance(v, str) and v \
                            and not v.startswith(("${", "{{", "ref:", "secret:")):
                        findings.append(Finding("error", "hardcoded_secret",
                            f"environments.{env_name}.variables.{k} looks like a "
                            f"hardcoded secret; reference a secret store instead."))


def validate(path: str, repo_root: str):
    findings: list[Finding] = []
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"ERROR: could not parse YAML: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(data, dict):
        print("ERROR: top level of config_pipe.yaml must be a mapping.", file=sys.stderr)
        sys.exit(2)

    check_required(data, findings)
    check_paths(data, findings, repo_root)
    check_enums(data, findings)
    custom_checks(data, findings)
    return findings


def main():
    ap = argparse.ArgumentParser(description="Validate an config_pipe.yaml file.")
    ap.add_argument("file", help="Path to config_pipe.yaml")
    ap.add_argument("--repo-root", default=None,
                    help="Repo root for resolving path fields (default: file's dir).")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = ap.parse_args()

    repo_root = args.repo_root or os.path.dirname(os.path.abspath(args.file))
    findings = validate(args.file, repo_root)

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if args.json:
        print(json.dumps({
            "valid": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "findings": [f.to_dict() for f in findings],
        }, indent=2))
    else:
        if not findings:
            print("✅ config_pipe.yaml is valid. No issues found.")
        else:
            for f in errors:
                print(f"❌ ERROR  [{f.code}] {f.message}")
            for f in warnings:
                print(f"⚠️  WARN   [{f.code}] {f.message}")
            print()
            status = "INVALID" if errors else "VALID (with warnings)"
            print(f"Result: {status} — {len(errors)} error(s), {len(warnings)} warning(s).")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
