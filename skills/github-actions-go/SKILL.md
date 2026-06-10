---
name: github-actions-go
description: >
  Use this skill whenever creating or modifying GitHub Actions workflows for Go projects. Triggers include:
  CI pipelines (lint, test, build), CD pipelines (deploy to Lambda or ECS via Terraform), release automation
  (semantic versioning, changelog, GitHub Releases), Go module publishing to pkg.go.dev, multi-environment
  promotion flows (dev → staging → production), OIDC authentication with AWS (no static credentials),
  or any mention of "GitHub Actions", "workflow YAML", "release", "tag", "OIDC", "pkg.go.dev", "go module
  proxy", "semantic release", "goreleaser", "changelog", "CI/CD" in a Go context. Apply before generating
  any `.github/workflows/*.yml` file.
---

# GitHub Actions for Go — CI, CD, Releases & pkg.go.dev

Act as a senior DevOps engineer specialising in Go release engineering. Every workflow decision here
affects developer velocity, security posture, and the reliability of the release signal. Be explicit
about permissions, secret handling, and the exact sequence of steps that gate a production deploy.

---

## Workflow Catalogue

```
.github/
└── workflows/
    ├── ci.yml              ← lint + test + build on every PR and push to main
    ├── release.yml         ← tag → GitHub Release → pkg.go.dev update
    ├── deploy-lambda.yml   ← CD: build artifact → update Lambda function code
    ├── deploy-ecs.yml      ← CD: build image → push ECR → update ECS service
    └── terraform.yml       ← plan on PR, apply on merge to main
```

---

## Workflow 1 — CI (Pull Request & Push)

Runs on every PR and every push to `main`. Must pass before merge.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read          # minimum required; never grant write unless needed

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true  # cancel stale runs on force-push

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod     # always read version from go.mod, not hardcoded
          cache: true

      - name: golangci-lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: v1.57.2            # pin exact version; update intentionally
          args: --timeout 5m

  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true

      - name: Run tests with race detector
        run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Check coverage threshold
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | tr -d '%')
          echo "Coverage: ${COVERAGE}%"
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage ${COVERAGE}% is below 80% threshold"
            exit 1
          fi

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.out
          retention-days: 7

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true

      - name: Build Go binary (Linux arm64)
        env:
          CGO_ENABLED: "0"
          GOOS: linux
          GOARCH: arm64
        run: go build -trimpath -ldflags="-s -w" -o dist/bootstrap ./cmd/api

      - name: Upload binary artifact
        uses: actions/upload-artifact@v4
        with:
          name: binary-${{ github.sha }}
          path: dist/bootstrap
          retention-days: 1
```

---

## Workflow 2 — Release (Semantic Versioning → GitHub Release → pkg.go.dev)

Triggered manually or by merging a release branch. Produces a signed GitHub Release and
notifies the Go module proxy so pkg.go.dev indexes the new version immediately.

```yaml
# .github/workflows/release.yml
name: Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: "Semantic version to release (e.g. v1.4.2)"
        required: true
        type: string
      prerelease:
        description: "Mark as pre-release"
        required: false
        type: boolean
        default: false

permissions:
  contents: write          # required to create tags and GitHub Releases
  id-token: write          # required for OIDC (if pushing artifacts to S3/ECR)

jobs:
  validate:
    name: Validate version
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.parse.outputs.version }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0    # full history needed for changelog generation

      - name: Validate semver format
        id: parse
        run: |
          VERSION="${{ inputs.version }}"
          if ! echo "$VERSION" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$'; then
            echo "Invalid version format: $VERSION — must match vMAJOR.MINOR.PATCH"
            exit 1
          fi
          # Ensure tag does not already exist
          if git tag | grep -q "^${VERSION}$"; then
            echo "Tag $VERSION already exists"
            exit 1
          fi
          echo "version=$VERSION" >> "$GITHUB_OUTPUT"

  test:
    name: Full test suite
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
      - run: go test -race ./...

  release:
    name: Create GitHub Release
    runs-on: ubuntu-latest
    needs: [validate, test]
    env:
      VERSION: ${{ needs.validate.outputs.version }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true

      # Build release binaries for all target platforms
      - name: Build release binaries
        run: |
          mkdir -p dist

          # Linux arm64 — Lambda / Graviton ECS (primary target)
          CGO_ENABLED=0 GOOS=linux GOARCH=arm64 \
            go build -trimpath \
              -ldflags="-s -w -X main.version=${{ env.VERSION }} -X main.commit=${{ github.sha }}" \
              -o dist/bootstrap-linux-arm64 ./cmd/api

          # Linux amd64 — fallback / x86 ECS
          CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
            go build -trimpath \
              -ldflags="-s -w -X main.version=${{ env.VERSION }} -X main.commit=${{ github.sha }}" \
              -o dist/bootstrap-linux-amd64 ./cmd/api

          # Package Lambda zips
          (cd dist && zip bootstrap-linux-arm64.zip bootstrap-linux-arm64)
          (cd dist && zip bootstrap-linux-amd64.zip bootstrap-linux-amd64)

      # Generate changelog from conventional commits since last tag
      - name: Generate changelog
        id: changelog
        run: |
          PREV_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
          if [ -z "$PREV_TAG" ]; then
            RANGE="HEAD"
          else
            RANGE="${PREV_TAG}..HEAD"
          fi

          CHANGELOG=$(git log "$RANGE" \
            --pretty=format:"- %s (%h)" \
            --no-merges \
            | grep -E "^- (feat|fix|perf|refactor|docs|chore|ci|build|test)" || true)

          # Write to file so multiline is handled correctly
          {
            echo "## What's Changed"
            echo ""
            echo "$CHANGELOG"
          } > /tmp/changelog.md

          echo "changelog_file=/tmp/changelog.md" >> "$GITHUB_OUTPUT"

      # Create and push the git tag
      - name: Tag commit
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git tag -a "${{ env.VERSION }}" -m "Release ${{ env.VERSION }}"
          git push origin "${{ env.VERSION }}"

      # Create the GitHub Release with binaries attached
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name:   ${{ env.VERSION }}
          name:       "Release ${{ env.VERSION }}"
          body_path:  ${{ steps.changelog.outputs.changelog_file }}
          prerelease: ${{ inputs.prerelease }}
          files: |
            dist/bootstrap-linux-arm64.zip
            dist/bootstrap-linux-amd64.zip
          token: ${{ secrets.GITHUB_TOKEN }}

  publish-module:
    name: Publish to pkg.go.dev
    runs-on: ubuntu-latest
    needs: [release]
    env:
      VERSION: ${{ needs.validate.outputs.version }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ env.VERSION }}   # checkout the tagged commit

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true

      # Verify the module is valid and all dependencies resolve correctly
      - name: Verify module
        run: |
          go mod verify
          go mod tidy
          git diff --exit-code go.sum   # fail if go.sum changed (dirty deps)

      # Trigger the Go module proxy to index the new version.
      # The proxy fetches the tag from GitHub and makes it available on pkg.go.dev.
      # GOPROXY=direct bypasses the cache and forces a fresh fetch of the new tag.
      - name: Notify Go module proxy (pkg.go.dev)
        env:
          MODULE_PATH: ${{ github.repository }}  # e.g. github.com/org/service
        run: |
          # Fetch the module through the proxy to trigger indexing
          GOPROXY=https://proxy.golang.org,direct \
            go list -m "github.com/${{ env.MODULE_PATH }}@${{ env.VERSION }}" 2>&1 || true

          # Hit the sum database to register the hash
          curl -sSf "https://sum.golang.org/lookup/github.com/${{ env.MODULE_PATH }}@${{ env.VERSION }}" \
            -o /dev/null --retry 3 --retry-delay 5 || true

          echo "Module github.com/${{ env.MODULE_PATH }}@${{ env.VERSION }} submitted to proxy."
          echo "It will appear on pkg.go.dev within a few minutes."
          echo "Direct link: https://pkg.go.dev/github.com/${{ env.MODULE_PATH }}@${{ env.VERSION }}"
```

---

## Workflow 3 — Deploy Lambda (CD)

Triggered automatically on push to `main` (after CI passes) or on a new release tag.
Uses OIDC — no static AWS credentials stored in GitHub Secrets.

```yaml
# .github/workflows/deploy-lambda.yml
name: Deploy Lambda

on:
  push:
    branches: [main]
  release:
    types: [published]

permissions:
  contents: read
  id-token: write    # required for OIDC token exchange with AWS

jobs:
  deploy:
    name: Deploy to ${{ matrix.environment }}
    runs-on: ubuntu-latest
    environment: ${{ matrix.environment }}   # maps to GitHub Environment (with approvals)

    strategy:
      matrix:
        include:
          - environment: dev
            aws_role: arn:aws:iam::111111111111:role/github-actions-deploy-dev
            function_name: orders-api-dev
          - environment: staging
            aws_role: arn:aws:iam::222222222222:role/github-actions-deploy-staging
            function_name: orders-api-staging
          # production only on release events
          - environment: production
            aws_role: arn:aws:iam::333333333333:role/github-actions-deploy-prod
            function_name: orders-api-production

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true

      # Authenticate to AWS via OIDC — zero static credentials
      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume:    ${{ matrix.aws_role }}
          aws-region:        us-east-1
          role-session-name: github-actions-${{ github.run_id }}

      - name: Build Lambda binary
        env:
          CGO_ENABLED: "0"
          GOOS: linux
          GOARCH: arm64
        run: |
          go build -trimpath \
            -ldflags="-s -w -X main.version=${{ github.ref_name }} -X main.commit=${{ github.sha }}" \
            -o dist/bootstrap ./cmd/api
          (cd dist && zip bootstrap.zip bootstrap)

      - name: Deploy to Lambda
        run: |
          aws lambda update-function-code \
            --function-name "${{ matrix.function_name }}" \
            --zip-file fileb://dist/bootstrap.zip \
            --architectures arm64 \
            --no-cli-pager

          # Wait for the update to complete before publishing alias
          aws lambda wait function-updated \
            --function-name "${{ matrix.function_name }}"

      - name: Publish Lambda version and update alias
        run: |
          VERSION=$(aws lambda publish-version \
            --function-name "${{ matrix.function_name }}" \
            --description "Deploy ${{ github.sha }}" \
            --query 'Version' --output text)

          aws lambda update-alias \
            --function-name "${{ matrix.function_name }}" \
            --name live \
            --function-version "$VERSION" \
            --no-cli-pager

          echo "Published version $VERSION, alias 'live' updated."

      - name: Smoke test (invoke function)
        run: |
          RESULT=$(aws lambda invoke \
            --function-name "${{ matrix.function_name }}:live" \
            --payload '{"httpMethod":"GET","path":"/health"}' \
            --query 'StatusCode' --output text \
            response.json)
          echo "Invoke status: $RESULT"
          if [ "$RESULT" != "200" ]; then
            echo "Smoke test failed — rolling back alias"
            aws lambda update-alias \
              --function-name "${{ matrix.function_name }}" \
              --name live \
              --function-version '$LATEST'
            exit 1
          fi
```

---

## Workflow 4 — Terraform Plan/Apply

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    paths: ["infra/**"]
  push:
    branches: [main]
    paths: ["infra/**"]

permissions:
  contents: read
  id-token: write
  pull-requests: write    # to post plan output as PR comment

jobs:
  terraform:
    name: ${{ github.event_name == 'pull_request' && 'Plan' || 'Apply' }}
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra/environments/${{ vars.TF_ENVIRONMENT }}

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~1.7"

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region:     us-east-1

      - name: Terraform Init
        run: terraform init -input=false

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        id: plan
        run: |
          terraform plan -input=false -no-color -out=tfplan 2>&1 | tee plan.txt
          echo "exitcode=$?" >> "$GITHUB_OUTPUT"

      # Post plan as PR comment for review
      - name: Post plan to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('infra/environments/${{ vars.TF_ENVIRONMENT }}/plan.txt', 'utf8');
            const truncated = plan.length > 60000 ? plan.slice(0, 60000) + '\n\n[truncated]' : plan;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Terraform Plan — \`${{ vars.TF_ENVIRONMENT }}\`\n\`\`\`hcl\n${truncated}\n\`\`\``
            });

      # Apply only on push to main (never on PR)
      - name: Terraform Apply
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: terraform apply -input=false -auto-approve tfplan
```

---

## OIDC Trust Policy (AWS Side)

Configure this IAM role in Terraform so GitHub Actions can assume it without static credentials:

```hcl
# modules/iam-github-oidc/main.tf

data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "github_actions" {
  name = "github-actions-deploy-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = data.aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          # Scope to specific repo and branch/tag; never allow all repos
          "token.actions.githubusercontent.com:sub" = [
            "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main",
            "repo:${var.github_org}/${var.github_repo}:ref:refs/tags/v*",
          ]
        }
      }
    }]
  })
}

# Attach only the permissions this role needs (Lambda update, ECR push, S3 artifact, etc.)
resource "aws_iam_role_policy" "deploy" {
  name   = "deploy-policy"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.deploy.json
}
```

---

## pkg.go.dev Publishing Rules

For a Go module to be discoverable and indexed on pkg.go.dev:

1. **Module path must match the GitHub repository URL**: `module github.com/org/repo` in `go.mod`
2. **Tag must be a valid semver with `v` prefix**: `v1.2.3`, never `1.2.3` or `release-1.2.3`
3. **For v2+, module path must include major version**: `module github.com/org/repo/v2`
4. **`go.sum` must be committed and clean**: the proxy validates checksums
5. **Tag must be pushed before calling the proxy**: the proxy fetches from the tag, not from a branch
6. **`LICENSE` file must exist at module root**: pkg.go.dev will not index modules without a license

```
# go.mod — v1 module (no path suffix needed)
module github.com/org/orders
go 1.22

# go.mod — v2+ module (path suffix required)
module github.com/org/orders/v2
go 1.22
```

Verify indexing manually after release:
```bash
# Force the proxy to fetch the new version
GOPROXY=https://proxy.golang.org,direct go list -m github.com/org/orders@v1.4.2

# Check if it appears on pkg.go.dev (may take 1-5 minutes)
open https://pkg.go.dev/github.com/org/orders@v1.4.2
```

---

## Reusable Workflow Pattern (mono-repo)

Extract common jobs as reusable workflows to avoid duplication across services:

```yaml
# .github/workflows/_reusable-go-build.yml
name: Reusable Go Build

on:
  workflow_call:
    inputs:
      go-version-file:
        type: string
        default: go.mod
      cmd-path:
        type: string
        required: true        # e.g. ./cmd/api
      artifact-name:
        type: string
        required: true
    outputs:
      artifact-name:
        value: ${{ inputs.artifact-name }}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: ${{ inputs.go-version-file }}
          cache: true
      - name: Build
        env: { CGO_ENABLED: "0", GOOS: linux, GOARCH: arm64 }
        run: |
          go build -trimpath -ldflags="-s -w" -o dist/bootstrap ${{ inputs.cmd-path }}
          (cd dist && zip bootstrap.zip bootstrap)
      - uses: actions/upload-artifact@v4
        with:
          name: ${{ inputs.artifact-name }}
          path: dist/bootstrap.zip
          retention-days: 1
```

Call the reusable workflow from a service:
```yaml
jobs:
  build:
    uses: ./.github/workflows/_reusable-go-build.yml
    with:
      cmd-path: ./cmd/api
      artifact-name: orders-api-${{ github.sha }}
```

---

## GitHub Actions Quality Checklist

- [ ] All workflows pin `actions/*` at exact SHA or major version tag (e.g. `@v4`)
- [ ] `permissions:` declared at workflow and job level — minimum required only
- [ ] No `secrets.*` containing AWS credentials — use OIDC (`id-token: write`)
- [ ] OIDC trust policy scoped to specific repo and branch/tag (no wildcards on repo)
- [ ] `concurrency:` with `cancel-in-progress: true` on CI to avoid stale runs
- [ ] `go-version-file: go.mod` used — never hardcode Go version in workflow
- [ ] golangci-lint version pinned exactly
- [ ] `go test -race ./...` in CI — never skip the race detector
- [ ] Coverage threshold enforced in CI
- [ ] Release workflow validates semver format before tagging
- [ ] Release workflow runs full test suite before creating tag
- [ ] `go mod verify` and `go mod tidy` + clean `go.sum` check in release
- [ ] Module path in `go.mod` matches GitHub repo URL
- [ ] `v` prefix on all semver tags (`v1.2.3`, not `1.2.3`)
- [ ] `LICENSE` file at module root (required for pkg.go.dev indexing)
- [ ] Lambda deploy waits for `function-updated` before publishing alias
- [ ] Smoke test after deploy with automatic alias rollback on failure
- [ ] Terraform plan posted as PR comment; apply only on merge to `main`
- [ ] Reusable workflows used for shared steps (mono-repo)
