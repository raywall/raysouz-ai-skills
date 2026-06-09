# AI Skills — README

Ecossistema de skills para desenvolvimento de serviços Go em AWS usando DDD, Clean Architecture,
resiliência, observabilidade, FinOps e exposição de dados para LLMs via MCP.

Compatível com **Claude Code**, **Devin** e **OpenAI Codex** (codex CLI).

---

## Skills Disponíveis

| Skill | Arquivo | Quando Usar |
|---|---|---|
| `custom-business-metrics` | `custom-business-metrics/SKILL.md` | Instrumentar métricas, desenhar dashboards, criar queries de widgets, usar filtros, trace e correlation id. |
| `ddd-context-mapping` | `ddd-context-mapping/SKILL.md` | Antes de qualquer código: domínios, bounded contexts, aggregates, eventos |
| `github-actions-go` | `github-actions-go/SKILL.md` | Workflows de CI, CD, releases semânticos, publicação no pkg.go.dev e OIDC com AWS. |
| `go-clean-architecture` | `go-clean-architecture/SKILL.md` | Estrutura de diretórios, camadas, ports & adapters, DI |
| `go-concurrency-patterns` | `go-concurrency-patterns/SKILL.md` | goroutines, channels, worker pool, pipeline, errgroup |
| `frontend-design` | `frontend-design/SKILL.md` | Design de interfaces frontend, componentes, UX patterns, acessibilidade e consistência visual. |
| `go-doc-standards` | `go-doc-standards/SKILL.md` | File headers, GoDoc, documentação de todos os identificadores exportados |
| `go-graphql-connector` | `go-graphql-connector/SKILL.md` | Criar `service.json`, `schema.json`, `connectors.json`, mocks, queries GraphQL e bootstrap local/Lambda do conector. |
| `go-test-excellence` | `go-test-excellence/SKILL.md` | Estratégias avançadas de teste em Go: pirâmide de testes, contract testing, mutation testing e qualidade de suite. |
| `go-testing-excellence` | `go-testing-excellence/SKILL.md` | TDD, table-driven tests, mocks, HTTP handler tests, benchmarks, fuzz tests, golden files, cobertura. |
| `go-microservices-aws` | `go-microservices-aws/SKILL.md` | Lambda vs ECS, resiliência, SQS/SNS/EventBridge |
| `mcp-llm-exposure` | `mcp-llm-exposure/SKILL.md` | Servidor MCP em Go, tools/resources/prompts, segurança, outputs LLM-friendly |
| `mobile-ios-design` | `mobile-ios-design/SKILL.md` | Design de apps iOS, padrões nativos UIKit/SwiftUI, HIG da Apple e experiência mobile. |
| `observability-finops` | `observability-finops/SKILL.md` | slog, OpenTelemetry, X-Ray, CloudWatch, SLOs, FinOps |
| `routing-slip-runtime` | `routing-slip-runtime/SKILL.md` | Gerar `config.yaml`, `main.go`, Lambda handler, configuração de trigger, state store, idempotência, métricas e MCP. |
| `routing-slip-workflow` | `routing-slip-workflow/SKILL.md` | Criar, revisar, compor ou explicar workflows YAML do `routing-slip-pattern`. |
| `terraform-aws-deploy` | `terraform-aws-deploy/SKILL.md` | Módulos Terraform para Lambda, ECS, DynamoDB, SQS, IAM least-privilege, remote state, FinOps tags e checkov. |
| `workflow-architecture` | `workflow-architecture/SKILL.md` | Projetar uma solução ponta a ponta usando os três projetos de forma integrada. |

---

## Ordem de Aplicação (Fluxo Padrão)

```
1.  ddd-context-mapping        → Estabelecer fronteiras de domínio
         ↓
2.  workflow-architecture      → Projetar a solução ponta a ponta (se houver orquestração)
         ↓
3.  go-clean-architecture      → Estruturar camadas do serviço
         ↓
4.  go-microservices-aws       → Decidir compute (Lambda/ECS) e integração assíncrona
         ↓
5.  routing-slip-workflow      → Modelar workflows YAML de orquestração (se aplicável)
         ↓
6.  routing-slip-runtime       → Gerar runtime do conector/handler (se aplicável)
         ↓
7.  go-graphql-connector       → Construir o conector GraphQL (se aplicável)
         ↓
8.  go-concurrency-patterns    → Aplicar concorrência segura onde necessário
         ↓
9.  observability-finops       → Instrumentar logging, tracing, métricas e custo
         ↓
10. custom-business-metrics    → Adicionar métricas de negócio e dashboards
         ↓
11. go-doc-standards           → Documentar todo código exportado
         ↓
12. go-testing-excellence    → Escrever e revisar testes (unit, integration, bench, fuzz)
         ↓
13. terraform-aws-deploy       → Provisionar infraestrutura AWS com Terraform
         ↓
14. github-actions-go          → Configurar CI/CD, releases e publicação no pkg.go.dev
         ↓
15. mcp-llm-exposure           → Expor dados para agentes LLM via MCP (se aplicável)
         ↓
16. go-test-excellence         → Aplicar estratégias avançadas de qualidade de suite de testes
         ↓
17. frontend-design            → Projetar interfaces frontend com UX patterns e acessibilidade (se aplicável)
         ↓
18. mobile-ios-design          → Projetar features iOS com padrões nativos UIKit/SwiftUI (se aplicável)
```

---

## Uso no Claude Code

### Estrutura de diretórios

Copie a pasta inteira de skills para dentro do repositório do serviço:

```
your-service/
├── .claude/
│   └── skills/
│       ├── custom-business-metrics/
│       │   └── SKILL.md
│       ├── ddd-context-mapping/
│       │   └── SKILL.md
│       ├── github-actions-go/
│       │   └── SKILL.md
│       ├── frontend-design/
│       │   └── SKILL.md
│       ├── go-clean-architecture/
│       │   └── SKILL.md
│       ├── go-concurrency-patterns/
│       │   └── SKILL.md
│       ├── go-doc-standards/
│       │   └── SKILL.md
│       ├── go-graphql-connector/
│       │   └── SKILL.md
│       ├── go-microservices-aws/
│       │   └── SKILL.md
│       ├── go-test-excellence/
│       │   └── SKILL.md
│       ├── go-testing-excellence/
│       │   └── SKILL.md
│       ├── mcp-llm-exposure/
│       │   └── SKILL.md
│       ├── mobile-ios-design/
│       │   └── SKILL.md
│       ├── observability-finops/
│       │   └── SKILL.md
│       ├── routing-slip-runtime/
│       │   └── SKILL.md
│       ├── routing-slip-workflow/
│       │   └── SKILL.md
│       ├── terraform-aws-deploy/
│       │   └── SKILL.md
│       └── workflow-architecture/
│           └── SKILL.md
├── internal/
├── cmd/
├── infra/
└── go.mod
```

### Arquivo CLAUDE.md (instrução global do projeto)

Crie `.claude/CLAUDE.md` na raiz do repositório para que o Claude Code carregue as skills automaticamente
a cada sessão:

```markdown
# Project Instructions

This is a Go service following DDD, Clean Architecture, and AWS best practices.

## Skills — Read Before Acting

Before generating any code, read the relevant skill files in `.claude/skills/`:

- Designing domains or service boundaries        → read `ddd-context-mapping/SKILL.md`
- Designing an end-to-end solution               → read `workflow-architecture/SKILL.md`
- Creating or modifying Go packages/layers       → read `go-clean-architecture/SKILL.md`
- AWS infrastructure or service communication    → read `go-microservices-aws/SKILL.md`
- Modeling orchestration workflows (YAML)        → read `routing-slip-workflow/SKILL.md`
- Implementing routing-slip runtime or handler   → read `routing-slip-runtime/SKILL.md`
- Building or extending a GraphQL connector      → read `go-graphql-connector/SKILL.md`
- Any goroutine, channel, or concurrent code     → read `go-concurrency-patterns/SKILL.md`
- Adding logs, traces, metrics, or cost tags     → read `observability-finops/SKILL.md`
- Adding business metrics or dashboards          → read `custom-business-metrics/SKILL.md`
- Writing or reviewing any exported Go symbol    → read `go-doc-standards/SKILL.md`
- Writing or reviewing any test file (*_test.go) → read `go-testing-excellence/SKILL.md`
- Applying advanced Go test quality strategies   → read `go-test-excellence/SKILL.md`
- Writing or modifying any Terraform (.tf) file  → read `terraform-aws-deploy/SKILL.md`
- Writing or modifying GitHub Actions workflows  → read `github-actions-go/SKILL.md`
- Building or extending the MCP server           → read `mcp-llm-exposure/SKILL.md`
- Designing or modifying frontend UI/UX          → read `frontend-design/SKILL.md`
- Designing or building iOS mobile features      → read `mobile-ios-design/SKILL.md`

## Non-Negotiable Standards

- All exported identifiers must have GoDoc-compliant comments (go-doc-standards)
- No layer may import a layer above it (go-clean-architecture)
- Every goroutine must have a guaranteed exit path (go-concurrency-patterns)
- All AWS resources must carry FinOps cost-allocation tags (observability-finops, terraform-aws-deploy)
- No static AWS credentials in GitHub Actions — use OIDC only (github-actions-go)
- No `"*"` in IAM resource or action fields (terraform-aws-deploy)
- Run `go test -race ./...` before considering any task complete
- Domain and application layers must maintain ≥ 80% test coverage (go-testing-excellence)
```

### Acionamento manual por prompt

Ao abrir uma sessão no Claude Code, você pode referenciar skills diretamente:

```
# Modelar um bounded context
Leia .claude/skills/ddd-context-mapping/SKILL.md e então modele o bounded context
de Pagamentos para o nosso sistema de e-commerce.
```

```
# Criar um novo serviço do zero
Leia as skills em .claude/skills/ (workflow-architecture, go-clean-architecture,
go-microservices-aws e go-doc-standards) e crie o scaffold completo do serviço
notification-sender como uma Lambda em Go.
```

```
# Provisionar infraestrutura
Leia .claude/skills/terraform-aws-deploy/SKILL.md e crie o módulo Terraform para
o serviço orders-api como Lambda arm64 com DynamoDB, SQS e IAM least-privilege.
```

```
# Configurar pipeline de release
Leia .claude/skills/github-actions-go/SKILL.md e crie os workflows de CI,
release semântico e deploy Lambda com OIDC para dev, staging e production.
```

```
# Criar um workflow de orquestração
Leia .claude/skills/routing-slip-workflow/SKILL.md e modele o workflow de
processamento de pedidos com as etapas: validar, reservar-estoque, cobrar, notificar.
```

```
# Criar testes para um use case
Leia .claude/skills/go-testing-excellence/SKILL.md e escreva os testes completos
para o PlaceOrderUseCase: table-driven, mocks de repositório e publisher, e benchmark.
```

```
# Adicionar métricas de negócio
Leia .claude/skills/custom-business-metrics/SKILL.md e instrumente as métricas
de GMV, taxa de conversão e abandono de carrinho no serviço de checkout.
```

### Configuração via settings.json (Claude Code)

Adicione ao `.claude/settings.json` para injetar contexto automaticamente:

```json
{
  "contextFiles": [
    ".claude/CLAUDE.md",
    ".claude/skills/ddd-context-mapping/SKILL.md",
    ".claude/skills/go-clean-architecture/SKILL.md",
    ".claude/skills/go-doc-standards/SKILL.md"
  ],
  "alwaysAllow": []
}
```

> **Dica de custo:** inclua no `contextFiles` apenas as skills do núcleo (ddd, clean-arch, doc-standards).
> As demais são carregadas sob demanda via prompt para não inflar o contexto de cada sessão.

---

## Uso no Devin

### Opção A — knowledge via `devin.toml`

Adicione cada skill como um documento de conhecimento no arquivo de configuração do projeto:

```toml
# devin.toml — na raiz do repositório

[knowledge]

  [[knowledge.documents]]
  path  = ".devin/skills/ddd-context-mapping/SKILL.md"
  title = "DDD Context Mapping"
  tags  = ["ddd", "domain", "bounded-context", "aggregate", "event"]

  [[knowledge.documents]]
  path  = ".devin/skills/workflow-architecture/SKILL.md"
  title = "Workflow Architecture"
  tags  = ["workflow", "architecture", "solution-design", "end-to-end", "integration"]

  [[knowledge.documents]]
  path  = ".devin/skills/go-clean-architecture/SKILL.md"
  title = "Go Clean Architecture"
  tags  = ["go", "architecture", "clean", "layers", "ports", "adapters"]

  [[knowledge.documents]]
  path  = ".devin/skills/go-microservices-aws/SKILL.md"
  title = "Go Microservices on AWS"
  tags  = ["go", "aws", "lambda", "ecs", "sqs", "sns", "resilience"]

  [[knowledge.documents]]
  path  = ".devin/skills/routing-slip-workflow/SKILL.md"
  title = "Routing Slip Workflow"
  tags  = ["routing-slip", "workflow", "yaml", "orchestration", "steps"]

  [[knowledge.documents]]
  path  = ".devin/skills/routing-slip-runtime/SKILL.md"
  title = "Routing Slip Runtime"
  tags  = ["routing-slip", "runtime", "lambda", "handler", "state-store", "idempotency"]

  [[knowledge.documents]]
  path  = ".devin/skills/go-graphql-connector/SKILL.md"
  title = "Go GraphQL Connector"
  tags  = ["go", "graphql", "connector", "schema", "service-json", "mock"]

  [[knowledge.documents]]
  path  = ".devin/skills/go-concurrency-patterns/SKILL.md"
  title = "Go Concurrency Patterns"
  tags  = ["go", "goroutine", "channel", "concurrency", "worker-pool"]

  [[knowledge.documents]]
  path  = ".devin/skills/observability-finops/SKILL.md"
  title = "Observability & FinOps"
  tags  = ["observability", "logging", "tracing", "metrics", "finops", "cost"]

  [[knowledge.documents]]
  path  = ".devin/skills/custom-business-metrics/SKILL.md"
  title = "Custom Business Metrics"
  tags  = ["metrics", "dashboard", "business", "widgets", "correlation-id", "trace"]

  [[knowledge.documents]]
  path  = ".devin/skills/go-doc-standards/SKILL.md"
  title = "Go Documentation Standards"
  tags  = ["go", "godoc", "documentation", "comments", "headers"]

  [[knowledge.documents]]
  path  = ".devin/skills/terraform-aws-deploy/SKILL.md"
  title = "Terraform AWS Deploy"
  tags  = ["terraform", "aws", "iac", "lambda", "ecs", "iam", "dynamodb", "finops", "remote-state"]

  [[knowledge.documents]]
  path  = ".devin/skills/github-actions-go/SKILL.md"
  title = "GitHub Actions for Go"
  tags  = ["github-actions", "ci", "cd", "release", "semver", "pkg.go.dev", "oidc", "goreleaser"]

  [[knowledge.documents]]
  path  = ".devin/skills/mcp-llm-exposure/SKILL.md"
  title = "MCP Server & LLM Exposure"
  tags  = ["mcp", "llm", "ai", "tools", "resources", "prompts"]

  [[knowledge.documents]]
  path  = ".devin/skills/go-test-excellence/SKILL.md"
  title = "Go Test Excellence"
  tags  = ["go", "testing", "quality", "mutation", "contract", "test-suite"]

  [[knowledge.documents]]
  path  = ".devin/skills/frontend-design/SKILL.md"
  title = "Frontend Design"
  tags  = ["frontend", "ui", "ux", "design", "components", "accessibility"]

  [[knowledge.documents]]
  path  = ".devin/skills/mobile-ios-design/SKILL.md"
  title = "Mobile iOS Design"
  tags  = ["ios", "mobile", "SwiftUI", "UIKit", "apple", "hig", "design"]
```

### Opção B — instrução no prompt de sessão (Devin Playbooks)

Crie um playbook `.devin/playbooks/new-go-service.md` para onboarding de novos serviços:

```markdown
# Playbook: New Go Service

## Before writing any code

1. Read `.devin/skills/ddd-context-mapping/SKILL.md`
   — identify bounded context, aggregates, and domain events for this service.

2. Read `.devin/skills/workflow-architecture/SKILL.md`
   — design the end-to-end solution if the service participates in an orchestrated workflow.

3. Read `.devin/skills/go-clean-architecture/SKILL.md`
   — scaffold the directory layout following the canonical structure.

4. Read `.devin/skills/go-microservices-aws/SKILL.md`
   — determine compute target (Lambda or ECS) and async communication pattern.

5. If the service is a workflow orchestrator:
   - Read `.devin/skills/routing-slip-workflow/SKILL.md` — model the workflow YAML.
   - Read `.devin/skills/routing-slip-runtime/SKILL.md` — generate the runtime handler.

6. If the service exposes or consumes a GraphQL API:
   - Read `.devin/skills/go-graphql-connector/SKILL.md` — build the connector.

## While writing code

- For any goroutine or channel           → read `go-concurrency-patterns/SKILL.md` first.
- For any log, metric, or trace          → read `observability-finops/SKILL.md` first.
- For business-level metrics/dashboards  → read `custom-business-metrics/SKILL.md`.
- For every exported Go identifier       → apply `go-doc-standards/SKILL.md` — no exceptions.
- For MCP tool or resource               → read `mcp-llm-exposure/SKILL.md`.

## While writing tests

- For any *_test.go file → read `go-testing-excellence/SKILL.md` — all 10 patterns apply.
- For advanced test quality → read `go-test-excellence/SKILL.md`.

## Infrastructure & delivery

- For any .tf file                       → read `terraform-aws-deploy/SKILL.md` first.
- For any .github/workflows/*.yml file   → read `github-actions-go/SKILL.md` first.
- For any frontend UI/UX work            → read `frontend-design/SKILL.md` first.
- For any iOS mobile feature             → read `mobile-ios-design/SKILL.md` first.

## Before marking task as complete

- [ ] `go build ./...` passes with zero errors
- [ ] `go test -race ./...` passes
- [ ] `golangci-lint run ./...` passes (godot + revive enabled)
- [ ] All exported identifiers have GoDoc comments
- [ ] All AWS resources have FinOps cost-allocation tags
- [ ] Business metrics instrumented and dashboard widgets documented
- [ ] `go test -race ./...` passes with zero races detected
- [ ] Coverage ≥ 80% on domain and application layers
- [ ] `terraform validate` and `tfsec` pass with no HIGH/CRITICAL findings
- [ ] GitHub Actions workflows use OIDC (no static AWS credentials)
- [ ] Release workflow validates semver, runs tests, and notifies Go module proxy
```

### Estrutura de diretórios para Devin

```
your-service/
├── .devin/
│   ├── skills/
│   │   ├── custom-business-metrics/SKILL.md
│   │   ├── ddd-context-mapping/SKILL.md
│   │   ├── github-actions-go/SKILL.md
│   │   ├── frontend-design/SKILL.md
│   │   ├── go-clean-architecture/SKILL.md
│   │   ├── go-concurrency-patterns/SKILL.md
│   │   ├── go-doc-standards/SKILL.md
│   │   ├── go-graphql-connector/SKILL.md
│   │   ├── go-microservices-aws/SKILL.md
│   │   ├── go-test-excellence/SKILL.md
│   │   ├── go-testing-excellence/SKILL.md
│   │   ├── mcp-llm-exposure/SKILL.md
│   │   ├── mobile-ios-design/SKILL.md
│   │   ├── observability-finops/SKILL.md
│   │   ├── routing-slip-runtime/SKILL.md
│   │   ├── routing-slip-workflow/SKILL.md
│   │   ├── terraform-aws-deploy/SKILL.md
│   │   └── workflow-architecture/SKILL.md
│   └── playbooks/
│       ├── new-go-service.md
│       ├── add-observability.md
│       ├── add-workflow.md
│       ├── add-graphql-connector.md
│       ├── provision-infra.md
│       └── setup-cicd.md
├── internal/
├── cmd/
├── infra/
└── go.mod
```

---

## Uso no OpenAI Codex (codex CLI)

### Opção A — arquivo `AGENTS.md` (carregado automaticamente)

O Codex CLI carrega automaticamente o arquivo `AGENTS.md` da raiz do repositório a cada sessão.
Use-o para referenciar as skills como instruções de contexto:

```markdown
<!-- AGENTS.md — raiz do repositório -->

# Agent Instructions

This repository implements Go microservices following DDD and Clean Architecture on AWS.

## Mandatory Reading — Skills

Read the relevant skill file before taking any action in that area.
Skill files are located in `.codex/skills/`.

| Task type | Skill to read |
|---|---|
| Domain modeling, service boundaries | `ddd-context-mapping/SKILL.md` |
| End-to-end solution design | `workflow-architecture/SKILL.md` |
| Package structure, layer separation | `go-clean-architecture/SKILL.md` |
| AWS compute, resilience, async messaging | `go-microservices-aws/SKILL.md` |
| Orchestration workflow modeling (YAML) | `routing-slip-workflow/SKILL.md` |
| Routing-slip runtime, Lambda handler | `routing-slip-runtime/SKILL.md` |
| GraphQL connector (schema, mocks, queries) | `go-graphql-connector/SKILL.md` |
| goroutines, channels, worker pools | `go-concurrency-patterns/SKILL.md` |
| Logging, tracing, metrics, cost tags | `observability-finops/SKILL.md` |
| Business metrics, dashboards, widgets | `custom-business-metrics/SKILL.md` |
| Any exported Go type, func, or method | `go-doc-standards/SKILL.md` |
| Any *_test.go file, TDD, benchmarks, fuzz | `go-testing-excellence/SKILL.md` |
| Advanced Go test quality strategies | `go-test-excellence/SKILL.md` |
| Any Terraform (.tf) file | `terraform-aws-deploy/SKILL.md` |
| Any GitHub Actions workflow (.yml) | `github-actions-go/SKILL.md` |
| MCP server, LLM tool/resource design | `mcp-llm-exposure/SKILL.md` |
| Frontend UI/UX design and components | `frontend-design/SKILL.md` |
| iOS mobile features and design | `mobile-ios-design/SKILL.md` |

## Coding Standards

- Layer imports flow inward only: infrastructure → application → domain
- Every goroutine must have a guaranteed termination path
- Every exported identifier must carry a GoDoc comment starting with its own name
- All AWS resources must carry the FinOps cost-allocation tags defined in observability-finops
- No `"*"` in IAM resource or action fields — always explicit ARN and action list
- Business metrics must follow the naming convention in custom-business-metrics
- Tests must pass with `go test -race ./...`
- Lint must pass with `golangci-lint run ./...`
- Terraform must pass `terraform validate` and `tfsec` with no HIGH/CRITICAL findings

## Forbidden Patterns

- `fmt.Println` in production code paths (use `slog.InfoContext`)
- `context.Background()` inside HTTP handlers or use cases (propagate the request context)
- Closing a channel from the receiver
- Importing a domain package from an infrastructure package
- Shared database tables across bounded contexts
- Metrics without correlation ID or trace ID linkage
- Static AWS credentials in GitHub Actions (use OIDC)
- Hardcoded AWS credentials or secrets in any Terraform file or tfvars
- IAM policies with `"Resource": "*"` or `"Action": "*"`
- Lambda functions without explicit timeout and DLQ
- Go module tags without the `v` prefix (e.g. `1.2.3` instead of `v1.2.3`)
- `time.Sleep` in tests for synchronisation (use channels or `require.Eventually`)
- Calling `time.Now()` in domain/application code without Clock injection
- Missing `t.Helper()` in test helper functions
```

### Opção B — profile global do Codex (`~/.codex/instructions.md`)

Para aplicar as instruções em todos os repositórios Go da máquina, adicione ao profile global:

```markdown
<!-- ~/.codex/instructions.md -->

## Go Projects — Skill System

When working in a Go repository that contains a `.codex/skills/` directory,
read the relevant `SKILL.md` files before acting:

- Domain/service design              → `ddd-context-mapping/SKILL.md`
- End-to-end solution design         → `workflow-architecture/SKILL.md`
- Package/layer structure            → `go-clean-architecture/SKILL.md`
- AWS services & resilience          → `go-microservices-aws/SKILL.md`
- Orchestration workflow (YAML)      → `routing-slip-workflow/SKILL.md`
- Routing-slip runtime/handler       → `routing-slip-runtime/SKILL.md`
- GraphQL connector                  → `go-graphql-connector/SKILL.md`
- Concurrency                        → `go-concurrency-patterns/SKILL.md`
- Observability & cost               → `observability-finops/SKILL.md`
- Business metrics & dashboards      → `custom-business-metrics/SKILL.md`
- Code documentation                 → `go-doc-standards/SKILL.md`
- Tests, TDD, benchmarks, fuzz         → `go-testing-excellence/SKILL.md`
- Advanced Go test quality            → `go-test-excellence/SKILL.md`
- Terraform infrastructure            → `terraform-aws-deploy/SKILL.md`
- GitHub Actions CI/CD & releases     → `github-actions-go/SKILL.md`
- MCP / LLM integration               → `mcp-llm-exposure/SKILL.md`
- Frontend UI/UX design               → `frontend-design/SKILL.md`
- iOS mobile design                   → `mobile-ios-design/SKILL.md`
```

### Opção C — injeção via `codex.json`

```json
{
  "model": "codex-1",
  "approval": "suggest",
  "notify": false,
  "contextPaths": [
    "AGENTS.md",
    ".codex/skills/ddd-context-mapping/SKILL.md",
    ".codex/skills/go-clean-architecture/SKILL.md",
    ".codex/skills/go-doc-standards/SKILL.md"
  ]
}
```

> **Dica de custo:** assim como no Claude Code, inclua no `contextPaths` apenas as skills do núcleo.
> As demais são carregadas sob demanda citando o caminho no prompt.

### Estrutura de diretórios para Codex

```
your-service/
├── AGENTS.md                               ← lido automaticamente pelo Codex CLI
├── codex.json                              ← configuração do agente
├── .codex/
│   └── skills/
│       ├── custom-business-metrics/SKILL.md
│       ├── ddd-context-mapping/SKILL.md
│       ├── github-actions-go/SKILL.md
│       ├── frontend-design/SKILL.md
│       ├── go-clean-architecture/SKILL.md
│       ├── go-concurrency-patterns/SKILL.md
│       ├── go-doc-standards/SKILL.md
│       ├── go-graphql-connector/SKILL.md
│       ├── go-microservices-aws/SKILL.md
│       ├── go-test-excellence/SKILL.md
│       ├── go-testing-excellence/SKILL.md
│       ├── mcp-llm-exposure/SKILL.md
│       ├── mobile-ios-design/SKILL.md
│       ├── observability-finops/SKILL.md
│       ├── routing-slip-runtime/SKILL.md
│       ├── routing-slip-workflow/SKILL.md
│       ├── terraform-aws-deploy/SKILL.md
│       └── workflow-architecture/SKILL.md
├── internal/
├── cmd/
├── infra/
└── go.mod
```

---

## Repositório Mono-Repo (múltiplos serviços)

Para repositórios com vários serviços, centralize as skills e referencie por caminho relativo:

```
monorepo/
├── .skills/                                ← skills centralizadas
│   ├── custom-business-metrics/SKILL.md
│   ├── ddd-context-mapping/SKILL.md
│   ├── frontend-design/SKILL.md
│   ├── github-actions-go/SKILL.md
│   ├── go-clean-architecture/SKILL.md
│   ├── go-concurrency-patterns/SKILL.md
│   ├── go-doc-standards/SKILL.md
│   ├── go-graphql-connector/SKILL.md
│   ├── go-microservices-aws/SKILL.md
│   ├── go-test-excellence/SKILL.md
│   ├── go-testing-excellence/SKILL.md
│   ├── mcp-llm-exposure/SKILL.md
│   ├── mobile-ios-design/SKILL.md
│   ├── observability-finops/SKILL.md
│   ├── routing-slip-runtime/SKILL.md
│   ├── routing-slip-workflow/SKILL.md
│   ├── terraform-aws-deploy/SKILL.md
│   └── workflow-architecture/SKILL.md
├── services/
│   ├── orders/
│   │   ├── .claude/
│   │   │   └── CLAUDE.md                  ← aponta para ../../.skills/
│   │   └── AGENTS.md                      ← aponta para ../../.skills/
│   └── payments/
│       ├── .claude/
│       │   └── CLAUDE.md
│       └── AGENTS.md
├── infra/                                  ← Terraform centralizado ou por serviço
│   ├── modules/
│   └── environments/
└── README.md
```

Exemplo de `CLAUDE.md` em serviço dentro de mono-repo:

```markdown
# Orders Service

Read skills from the monorepo root before acting:
- Domain design            → `../../.skills/ddd-context-mapping/SKILL.md`
- Solution architecture    → `../../.skills/workflow-architecture/SKILL.md`
- Architecture layers      → `../../.skills/go-clean-architecture/SKILL.md`
- AWS & resilience         → `../../.skills/go-microservices-aws/SKILL.md`
- Workflow orchestration   → `../../.skills/routing-slip-workflow/SKILL.md`
- Routing-slip runtime     → `../../.skills/routing-slip-runtime/SKILL.md`
- GraphQL connector        → `../../.skills/go-graphql-connector/SKILL.md`
- Concurrency              → `../../.skills/go-concurrency-patterns/SKILL.md`
- Observability & cost     → `../../.skills/observability-finops/SKILL.md`
- Business metrics         → `../../.skills/custom-business-metrics/SKILL.md`
- Documentation            → `../../.skills/go-doc-standards/SKILL.md`
- Tests & TDD              → `../../.skills/go-testing-excellence/SKILL.md`
- Advanced test quality    → `../../.skills/go-test-excellence/SKILL.md`
- Terraform infrastructure → `../../.skills/terraform-aws-deploy/SKILL.md`
- GitHub Actions CI/CD     → `../../.skills/github-actions-go/SKILL.md`
- MCP / LLM exposure       → `../../.skills/mcp-llm-exposure/SKILL.md`
- Frontend UI/UX           → `../../.skills/frontend-design/SKILL.md`
- iOS mobile design        → `../../.skills/mobile-ios-design/SKILL.md`
```

---

## Requisitos de Ambiente

| Componente | Versão mínima |
|---|---|
| Go | 1.22+ |
| AWS SDK for Go | v2 (aws-sdk-go-v2) |
| OpenTelemetry Go | v1.x |
| golangci-lint | v1.57+ |
| Terraform | 1.7+ |
| tfsec / checkov | latest |
| Claude Code CLI | latest |
| Devin | plano Teams ou Enterprise |
| Codex CLI | latest (`npm i -g @openai/codex`) |