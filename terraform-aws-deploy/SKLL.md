---
name: terraform-aws-deploy
description: >
  Use this skill whenever writing or reviewing Terraform code for deploying Go services on AWS. Triggers
  include: creating or modifying Terraform modules, defining AWS resources (Lambda, ECS/Fargate, API Gateway,
  DynamoDB, SQS, SNS, EventBridge, S3, IAM, VPC, CloudWatch, ACM, Route53, ElastiCache), structuring
  Terraform workspaces or environments, managing remote state (S3 + DynamoDB lock), designing module
  hierarchies, writing variable/output definitions, or any mention of "terraform", "tfvars", "module",
  "remote state", "workspace", "plan", "apply", "IAM role", "least privilege", "infrastructure as code"
  in an AWS context. Apply before generating any .tf file.
---

# Terraform AWS Deploy

Act as a senior infrastructure engineer with deep AWS and Terraform expertise. Infrastructure decisions
made here affect security posture, blast radius, cost, and team velocity for years. Be explicit about
every structural and security decision; never take shortcuts on IAM or state management.

---

## Project Layout

Every service follows the same Terraform layout. Consistency across services is non-negotiable —
it enables shared tooling, reviewers, and CI pipelines.

```
infra/
├── modules/                          ← reusable, service-agnostic building blocks
│   ├── lambda-service/               ← Lambda + IAM + CloudWatch + optional API GW
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md                 ← module inputs/outputs always documented
│   ├── ecs-service/                  ← ECS Fargate + ALB + IAM + CloudWatch
│   ├── dynamodb-table/               ← table + autoscaling + backup + FinOps tags
│   ├── sqs-queue/                    ← queue + DLQ + policy
│   ├── sns-topic/                    ← topic + subscriptions + policy
│   └── eventbridge-rule/             ← rule + target + IAM
├── environments/
│   ├── dev/
│   │   ├── main.tf                   ← calls modules with dev-specific var values
│   │   ├── variables.tf
│   │   ├── terraform.tfvars          ← committed; no secrets
│   │   ├── backend.tf                ← S3 remote state config for dev
│   │   └── outputs.tf
│   ├── staging/
│   └── production/
└── shared/
    ├── iam-baseline/                 ← org-wide IAM policies, SCPs references
    └── networking/                   ← VPC, subnets, security groups (if shared)
```

---

## Phase 1 — Remote State (Do This First)

Never use local state for team projects. Configure S3 + DynamoDB locking before writing any resource.

```hcl
# environments/production/backend.tf
terraform {
  backend "s3" {
    bucket         = "myorg-terraform-state-prod"
    key            = "services/orders/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "myorg-terraform-locks"   # partition key: LockID (String)
    kms_key_id     = "arn:aws:kms:us-east-1:123456789:key/mrk-abc123"
  }
}
```

Bootstrap the state bucket once (do not manage it with Terraform itself):

```bash
# Run once per AWS account — do NOT put this in a Terraform module
aws s3api create-bucket \
  --bucket myorg-terraform-state-prod \
  --region us-east-1 \
  --create-bucket-configuration LocationConstraint=us-east-1

aws s3api put-bucket-versioning \
  --bucket myorg-terraform-state-prod \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket myorg-terraform-state-prod \
  --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms"}}]}'

aws dynamodb create-table \
  --table-name myorg-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

---

## Phase 2 — Provider & Version Pinning

```hcl
# environments/production/main.tf

terraform {
  required_version = ">= 1.7.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"      # minor updates allowed; never unpinned
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.finops_tags   # applied to every resource automatically
  }

  # Never hardcode credentials — use OIDC (GitHub Actions) or instance profile
}
```

---

## Phase 3 — FinOps Tags (Required on Every Resource)

Define tags as locals; apply via `provider default_tags` so they propagate to all resources:

```hcl
# environments/production/main.tf

locals {
  finops_tags = {
    service      = var.service_name        # e.g. "orders"
    team         = var.team_name           # e.g. "platform"
    environment  = var.environment         # production | staging | dev
    cost-center  = var.cost_center         # e.g. "engineering/backend"
    bounded-ctx  = var.bounded_context     # DDD context name
    managed-by   = "terraform"
    repo         = var.repo_url            # e.g. "github.com/org/orders"
  }
}
```

---

## Phase 4 — IAM: Least Privilege

Every Lambda and ECS task gets its own IAM role. Never share roles across services.

```hcl
# modules/lambda-service/main.tf

# Execution role — only Lambda service can assume it
resource "aws_iam_role" "lambda_exec" {
  name               = "${var.function_name}-exec"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Attach only the minimum managed policies
resource "aws_iam_role_policy_attachment" "basic_exec" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy for service-specific permissions — explicit allow only
resource "aws_iam_role_policy" "service_policy" {
  name   = "${var.function_name}-policy"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.service_permissions.json
}

data "aws_iam_policy_document" "service_permissions" {
  # DynamoDB — table-scoped, not account-wide
  statement {
    sid     = "DynamoDBAccess"
    effect  = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
      "dynamodb:TransactWriteItems",
    ]
    resources = [
      var.dynamodb_table_arn,
      "${var.dynamodb_table_arn}/index/*",
    ]
  }

  # SQS — queue-scoped
  statement {
    sid     = "SQSConsume"
    effect  = "Allow"
    actions = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [var.sqs_queue_arn]
  }

  # Secrets Manager — secret-scoped, not wildcard
  statement {
    sid     = "SecretsAccess"
    effect  = "Allow"
    actions = ["secretsmanager:GetSecretValue"]
    resources = [var.secret_arn]
  }
}
```

IAM rules:
- No `"*"` in `resources` — always scope to the specific ARN
- No `"*"` in `actions` — always list explicit actions
- No `AdministratorAccess` or `PowerUserAccess` on service roles
- Use `aws_iam_policy_document` data source (not inline JSON strings)
- Separate `assume_role_policy` from permissions policy

---

## Phase 5 — Lambda Module

```hcl
# modules/lambda-service/main.tf

resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = "bootstrap"           # Go binary compiled as bootstrap
  runtime       = "provided.al2023"     # Amazon Linux 2023 — required for Go
  architectures = ["arm64"]             # Graviton2: 20% cheaper, faster for Go
  filename      = var.artifact_path     # path to the zip produced by CI

  memory_size = var.memory_mb           # default: 256; tune with Lambda Power Tuning
  timeout     = var.timeout_seconds     # always explicit; never leave at 3s default

  reserved_concurrent_executions = var.reserved_concurrency   # -1 = unreserved

  environment {
    variables = var.environment_variables
  }

  tracing_config {
    mode = "Active"                     # X-Ray active tracing always on
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn  # DLQ always configured
  }

  lifecycle {
    ignore_changes = [filename]         # CI updates the artifact; Terraform manages config
  }
}

# Dead-letter queue for async invocation failures
resource "aws_sqs_queue" "dlq" {
  name                      = "${var.function_name}-dlq"
  message_retention_seconds = 1209600   # 14 days
  kms_master_key_id         = "alias/aws/sqs"
}

# CloudWatch Log Group — explicit retention; never let logs grow forever
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days   # default: 30
  kms_key_id        = var.kms_key_arn
}
```

### Lambda SQS Event Source

```hcl
resource "aws_lambda_event_source_mapping" "sqs" {
  event_source_arn                   = var.sqs_queue_arn
  function_name                      = aws_lambda_function.this.arn
  batch_size                         = var.batch_size          # default: 10
  maximum_batching_window_in_seconds = var.batching_window     # default: 5
  bisect_batch_on_function_error     = true                    # split batch on error
  function_response_types            = ["ReportBatchItemFailures"]

  scaling_config {
    maximum_concurrency = var.max_concurrency   # prevent runaway scaling
  }
}
```

---

## Phase 6 — ECS Fargate Module

```hcl
# modules/ecs-service/main.tf

resource "aws_ecs_task_definition" "this" {
  family                   = var.service_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu        # e.g. 256, 512, 1024
  memory                   = var.task_memory     # e.g. 512, 1024, 2048
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name      = var.service_name
    image     = "${var.ecr_repository_url}:${var.image_tag}"
    essential = true

    portMappings = [{ containerPort = var.container_port, protocol = "tcp" }]

    environment = [for k, v in var.env_vars : { name = k, value = v }]
    secrets     = [for k, v in var.secrets : { name = k, valueFrom = v }]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = var.service_name
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -sf http://localhost:${var.container_port}/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 10
    }
  }])
}

resource "aws_ecs_service" "this" {
  name                               = var.service_name
  cluster                            = var.ecs_cluster_arn
  task_definition                    = aws_ecs_task_definition.this.arn
  desired_count                      = var.desired_count
  launch_type                        = "FARGATE"
  platform_version                   = "LATEST"
  health_check_grace_period_seconds  = 60

  deployment_circuit_breaker {
    enable   = true
    rollback = true       # auto-rollback on deployment failure
  }

  deployment_controller { type = "ECS" }

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.service.id]
    assign_public_ip = false   # always private; access via ALB
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = var.service_name
    container_port   = var.container_port
  }

  lifecycle {
    ignore_changes = [task_definition, desired_count]  # managed by CI/CD
  }
}
```

---

## Phase 7 — DynamoDB Module

```hcl
# modules/dynamodb-table/main.tf

resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = var.billing_mode    # PAY_PER_REQUEST (default) or PROVISIONED

  hash_key  = var.hash_key
  range_key = var.range_key          # optional

  dynamic "attribute" {
    for_each = var.attributes
    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  dynamic "global_secondary_index" {
    for_each = var.global_secondary_indexes
    content {
      name            = global_secondary_index.value.name
      hash_key        = global_secondary_index.value.hash_key
      range_key       = global_secondary_index.value.range_key
      projection_type = global_secondary_index.value.projection_type
    }
  }

  ttl {
    attribute_name = var.ttl_attribute   # always set; allows FinOps TTL cleanup
    enabled        = var.ttl_attribute != ""
  }

  point_in_time_recovery { enabled = var.environment == "production" }

  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  deletion_protection_enabled = var.environment == "production"
}
```

---

## Phase 8 — Variables & Outputs Conventions

```hcl
# modules/lambda-service/variables.tf

variable "function_name" {
  description = "Name of the Lambda function. Must be unique within the AWS account/region."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,62}$", var.function_name))
    error_message = "function_name must be lowercase alphanumeric with hyphens, 2-63 chars."
  }
}

variable "memory_mb" {
  description = "Lambda memory allocation in MB. Tune using AWS Lambda Power Tuning."
  type        = number
  default     = 256

  validation {
    condition     = var.memory_mb >= 128 && var.memory_mb <= 10240 && var.memory_mb % 64 == 0
    error_message = "memory_mb must be between 128 and 10240, in multiples of 64."
  }
}

variable "environment" {
  description = "Deployment environment. Controls deletion protection, backups, and log retention."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "environment must be one of: dev, staging, production."
  }
}
```

```hcl
# modules/lambda-service/outputs.tf

output "function_arn" {
  description = "ARN of the Lambda function. Use this to configure event source mappings."
  value       = aws_lambda_function.this.arn
}

output "function_name" {
  description = "Name of the Lambda function. Use this in CI/CD update-function-code calls."
  value       = aws_lambda_function.this.function_name
}

output "execution_role_arn" {
  description = "ARN of the Lambda execution role. Use this to grant additional permissions."
  value       = aws_iam_role.lambda_exec.arn
}

output "log_group_name" {
  description = "CloudWatch Log Group name for this function. Use in dashboard and alarm definitions."
  value       = aws_cloudwatch_log_group.lambda.name
}
```

Rules:
- Every `variable` block must have `description` and `type`
- Every `variable` with constrained values must have a `validation` block
- Every `output` block must have `description`
- Never use `sensitive = true` as a substitute for proper secrets management

---

## Phase 9 — Secrets Management

Never put secrets in `terraform.tfvars` or environment variables in plain text:

```hcl
# Reference secrets from AWS Secrets Manager — never store values in Terraform state
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "/${var.environment}/${var.service_name}/db-password"
}

# Pass to Lambda as a secret reference (fetched at cold start by the runtime)
# NOT as an environment variable value (which appears in state and CloudTrail)
resource "aws_lambda_function" "this" {
  # ...
  environment {
    variables = {
      DB_SECRET_ARN = data.aws_secretsmanager_secret_version.db_password.arn
    }
  }
}
```

The Go service retrieves the secret at startup:
```go
// Secrets are fetched once at cold start and cached; never read from env vars directly.
val, err := svc.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{
    SecretId: aws.String(os.Getenv("DB_SECRET_ARN")),
})
```

---

## Terraform Quality Checklist

Before committing any `.tf` file:

- [ ] Remote state configured with S3 + DynamoDB lock
- [ ] Provider version pinned with `~>` constraint
- [ ] `default_tags` set on the AWS provider with all FinOps tags
- [ ] Every IAM role is service-specific (no shared roles)
- [ ] No `"*"` in IAM `resources` or `actions`
- [ ] Every Lambda uses `provided.al2023` runtime and `arm64` architecture
- [ ] Every Lambda has explicit `timeout`, `memory_size`, and `reserved_concurrent_executions`
- [ ] Every Lambda has a DLQ configured
- [ ] Every Lambda has `tracing_config { mode = "Active" }` for X-Ray
- [ ] Every CloudWatch Log Group has explicit `retention_in_days`
- [ ] Every DynamoDB table has `ttl`, `point_in_time_recovery`, and `server_side_encryption`
- [ ] Production DynamoDB tables have `deletion_protection_enabled = true`
- [ ] ECS services have `deployment_circuit_breaker` with `rollback = true`
- [ ] No secrets in `.tfvars` or Lambda environment variable values
- [ ] Every `variable` has `description`, `type`, and `validation` where applicable
- [ ] Every `output` has `description`
- [ ] `terraform fmt -check` passes
- [ ] `terraform validate` passes
- [ ] `tfsec` or `checkov` scan passes with no HIGH/CRITICAL findings
