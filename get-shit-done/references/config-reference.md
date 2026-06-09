# Config Reference

## Purpose

`..config.yaml` lives at the repo root and serves two jobs:

1. **Application metadata** — identity of the service (name, owner, type, runtime).
2. **CI/CD operations** — the ordered stages that build, test, and deploy it.
3. **Tests settings** — 
4. **Security settings** — 
5. **Account settings** — 

## Expected structure

```yaml
# ── Application metadata ────────────────────────────────
application:
  name: <service-name>            # unique service identifier
  owner: <team-or-squad>          # owning team
  type: <service|worker|cron|...> # what kind of workload this is
  runtime: <language+version>     # e.g. python-3.12, node-20, go-1.22

# ── Build / artifact configuration ──────────────────────
build:
  context: <APPLICATION_DIR>      # where the build runs
  dockerfile: <path/to/Dockerfile>
  artifact: <image-name>          # produced image / package name

# ── Infrastructure linkage ──────────────────────────────
infrastructure:
  terraform_dir: <TERRAFORM_DIR>  # ties pipeline to the IaC folder
  backend: <state-backend-ref>

# ── CI/CD pipeline ──────────────────────────────────────
pipeline:
  trigger:
    on: [<push|pull_request|tag>]
    branches: [<main, release/*>]
  stages:
    - name: <build>
      run: <command>
    - name: <test>
      run: <command>
    - name: <deploy>
      environment: <dev|stg|prd>
      run: <command>
      requires_approval: <true|false>

# ── Environments ────────────────────────────────────────
environments:
  <dev>:
    variables: { <KEY>: <value> }
  <prd>:
    variables: { <KEY>: <value> }
```

## What must be configured for a new service

When documenting a repo, verify each of these is present and sensible. Flag any
that are missing or still placeholder:

1. `application.name` — must be unique and match the convention in `repo-conventions.md`.
2. `application.owner` — a real team, not a default.
3. `build.context` / `build.dockerfile` — must point at the real application dir.
4. `infrastructure.terraform_dir` — must point at the real Terraform folder.
5. `pipeline.trigger` — which events/branches start the pipeline.
6. `pipeline.stages` — at minimum build → test → deploy, in order.
7. `environments` — every environment referenced by a stage must be defined here.
8. Secrets/variables — confirm none are hardcoded; they should reference a secret store.

## Validating fulfillment

Do not validate by hand. Run the bundled validator, which encodes these rules
with per-rule severity (error vs. warning) and adds cross-reference checks:

```bash
python scripts/validate_config.py <.config.yaml> --repo-root <repo-root>
```

The "what must be configured" list above is mirrored in the script's `RULES`
section. **Keep the two in sync:** when you change a rule here, change it there
(and vice versa). The script is what determines pass/fail; this doc explains why.

## Common misconfigurations to call out

- `terraform_dir` pointing at a path that doesn't exist.
- A deploy stage targeting an environment not defined under `environments`.
- Production deploy with `requires_approval` unset or false.
- Hardcoded credentials in `variables`.

> Replace this list with the real validation rules `iup` enforces.
