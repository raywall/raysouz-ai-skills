# Repository Conventions

## Standard layout

A repository following this convention looks roughly like this:

```
<repo-root>/
├── .config.yaml              # App metadata + CI/CD definition (always at root)
├── <APPLICATION_DIR>/        # The service source code  — e.g. "app/" or "src/"
│   ├── <ENTRYPOINT>          # e.g. "main.py", "index.ts", "cmd/server/main.go"
│   ├── <CONFIG_LOCATION>     # where runtime config lives
│   └── ...
├── <TERRAFORM_DIR>/          # Infrastructure as code — e.g. "infra/" or "terraform/"
│   ├── <ENV_LAYOUT>          # how environments are separated (folders? workspaces? tfvars?)
│   └── ...
├── <TESTS_DIR>/              # optional — where tests live
└── <DOCS_DIR>/               # optional — existing docs
```

## Role mapping

When inspecting a repo, map what you find onto these roles:

| Role | Expected location | What it contains |
|------|-------------------|------------------|
| Application code | `<APPLICATION_DIR>` | The service itself: handlers, business logic, models |
| Entrypoint | `<APPLICATION_DIR>/<ENTRYPOINT>` | Where execution starts |
| Infrastructure | `<TERRAFORM_DIR>` | Terraform defining compute, networking, data stores |
| Environment config | `<ENV_LAYOUT>` | Per-environment values (dev/staging/prod) |
| Pipeline definition | `.config.yaml` (root) | App identity + CI/CD stages |

## Conventions to capture (fill these in)

- **Language(s) / framework(s):** `<e.g. Python + FastAPI, Go, Node + Express>`
- **How the application is built:** `<build command / Dockerfile location>`
- **Where the Terraform state lives:** `<remote backend? S3? Terraform Cloud?>`
- **Environment naming:** `<e.g. dev, stg, prd>`
- **Deploy target:** `<e.g. Kubernetes (EKS), ECS, Lambda, plain VMs>`
- **Naming rules:** `<service naming, resource prefixes, tagging requirements>`

## Known deviations / exceptions

`<List any repos or teams that legitimately diverge from the standard, so the skill
doesn't flag them as errors.>`
