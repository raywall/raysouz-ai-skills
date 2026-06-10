---
name: observability-finops
description: >
  Use this skill when adding observability or cost-awareness to any Go service on AWS. Triggers include:
  structured logging, distributed tracing, metrics emission, OpenTelemetry setup, CloudWatch configuration,
  X-Ray, Prometheus, dashboards, alerting, cost attribution tags, rightsizing, or any mention of "observability",
  "logging", "tracing", "metrics", "OTEL", "OpenTelemetry", "X-Ray", "CloudWatch", "FinOps", "cost",
  "rightsizing", "tags", "SLO", "SLI", "alert", or "dashboard" in the context of Go services. Apply before
  instrumenting any service to ensure consistent signal naming and cost tagging from day one.
---

# Observability & FinOps for Go Services on AWS

Act as a platform engineering and cloud economics expert. Observability is not optional telemetry — it is the
control plane for production systems. FinOps discipline starts at code level, not in the billing console.
Instrument everything from the first line; retrofitting is 10× more expensive.

---

## Observability Pillars

```
Logs   → What happened?         → structured JSON via slog
Traces → Where did time go?     → OpenTelemetry → AWS X-Ray / Grafana Tempo
Metrics → How is the system behaving? → OpenTelemetry → CloudWatch / Prometheus
```

---

## Phase 1 — Structured Logging (slog)

Use Go's standard `log/slog` package. Never use `fmt.Println` or unstructured loggers in production.

### Logger Setup

```go
// Package logger provides a configured slog.Logger for production use.
// All log entries include service, environment, and version fields by default.
package logger

// Config holds logger configuration loaded from environment.
type Config struct {
    ServiceName string
    Environment string // production | staging | development
    Version     string
    Level       slog.Level
}

// New creates a production-ready structured JSON logger with default attributes.
// The returned logger should be stored in a package-level var or injected via DI.
func New(cfg Config) *slog.Logger {
    h := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level:     cfg.Level,
        AddSource: cfg.Environment != "production",  // source location in non-prod
    })
    return slog.New(h).With(
        slog.String("service",     cfg.ServiceName),
        slog.String("environment", cfg.Environment),
        slog.String("version",     cfg.Version),
    )
}
```

### Logging Conventions

```go
// Log levels:
// Debug — detailed diagnostic info (disabled in production)
// Info  — significant events: service started, order placed, job completed
// Warn  — recoverable anomalies: retry attempt, cache miss, degraded mode
// Error — unrecoverable failures requiring attention

// Always log with context to correlate with traces.
logger.InfoContext(ctx, "order placed",
    slog.String("orderId",    order.ID.String()),
    slog.String("customerId", order.CustomerID.String()),
    slog.Float64("totalUSD",  order.Total.ToFloat()),
    slog.Int("itemCount",     len(order.Items)),
)

logger.ErrorContext(ctx, "payment failed",
    slog.String("orderId", order.ID.String()),
    slog.String("error",   err.Error()),
    slog.String("code",    paymentErr.Code),
)
```

### Required Fields per Log Entry

| Field | Type | Source |
|---|---|---|
| `service` | string | Config — injected at startup |
| `environment` | string | Config |
| `version` | string | Build-time variable |
| `traceId` | string | Extracted from OTEL context |
| `spanId` | string | Extracted from OTEL context |
| `requestId` | string | From HTTP header / event ID |

### Trace/Log Correlation Middleware

```go
// LoggingMiddleware enriches every log entry with the OTEL trace and span IDs.
// Place this middleware after the tracing middleware in the chain.
func LoggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            span := trace.SpanFromContext(r.Context())
            sc   := span.SpanContext()

            reqLogger := logger.With(
                slog.String("traceId",   sc.TraceID().String()),
                slog.String("spanId",    sc.SpanID().String()),
                slog.String("requestId", r.Header.Get("X-Request-ID")),
                slog.String("method",    r.Method),
                slog.String("path",      r.URL.Path),
            )
            ctx := context.WithValue(r.Context(), loggerKey{}, reqLogger)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

---

## Phase 2 — Distributed Tracing (OpenTelemetry → X-Ray)

### OTEL Setup

```go
// Package tracing initialises the OpenTelemetry SDK for AWS X-Ray export.
package tracing

// Init configures the global TracerProvider with AWS X-Ray as the backend.
// Call once at startup. The returned shutdown function must be called before exit.
func Init(ctx context.Context, cfg Config) (shutdown func(context.Context) error, err error) {
    exporter, err := otlptracehttp.New(ctx,
        otlptracehttp.WithEndpoint(cfg.OTELCollectorEndpoint),
        otlptracehttp.WithInsecure(),  // TLS at collector level
    )
    if err != nil { return nil, fmt.Errorf("tracing exporter: %w", err) }

    idgen := xray.NewIDGenerator()  // AWS X-Ray compatible trace IDs

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithIDGenerator(idgen),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName(cfg.ServiceName),
            semconv.ServiceVersion(cfg.Version),
            semconv.DeploymentEnvironment(cfg.Environment),
            attribute.String("aws.region", cfg.AWSRegion),
        )),
        sdktrace.WithSampler(sdktrace.ParentBased(
            sdktrace.TraceIDRatioBased(cfg.SampleRate),  // e.g. 0.1 = 10%
        )),
    )

    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(xray.Propagator{})  // X-Ray propagation format
    return tp.Shutdown, nil
}
```

### Span Conventions

```go
// Always name spans as: "package.Type.Method" or "operation.resource"
tracer := otel.Tracer("github.com/org/service/internal/application")

func (uc *PlaceOrderUseCase) Execute(ctx context.Context, in PlaceOrderInput) (PlaceOrderOutput, error) {
    ctx, span := tracer.Start(ctx, "PlaceOrderUseCase.Execute",
        trace.WithAttributes(
            attribute.String("order.customer_id", in.CustomerID),
            attribute.Int("order.item_count", len(in.Items)),
        ),
    )
    defer span.End()

    // Record errors on the span
    if err := validate(in); err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return PlaceOrderOutput{}, err
    }

    span.SetAttributes(attribute.String("order.id", order.ID.String()))
    return output, nil
}
```

---

## Phase 3 — Metrics (OpenTelemetry → CloudWatch)

### Metric Naming Convention

```
{service}.{noun}.{verb}_{unit}
Examples:
  orders.order.placed_total          counter
  orders.payment.duration_ms         histogram
  orders.inventory.available_items   gauge
  orders.sqs.lag_seconds             gauge
```

### Metric Setup

```go
// Package metrics registers all service-level OpenTelemetry metrics.
package metrics

// Instruments holds all metric instruments for the Orders service.
// Initialise once at startup and pass via DI.
type Instruments struct {
    OrdersPlaced    metric.Int64Counter
    PaymentDuration metric.Float64Histogram
    SQSLag          metric.Float64Gauge
}

// New creates and registers all metric instruments.
// Returns an error if any instrument cannot be created.
func New(meter metric.Meter) (*Instruments, error) {
    placed, err := meter.Int64Counter("orders.order.placed_total",
        metric.WithDescription("Total number of orders successfully placed."),
        metric.WithUnit("{order}"),
    )
    if err != nil { return nil, err }

    duration, err := meter.Float64Histogram("orders.payment.duration_ms",
        metric.WithDescription("End-to-end payment processing latency in milliseconds."),
        metric.WithUnit("ms"),
        metric.WithExplicitBucketBoundaries(10, 25, 50, 100, 250, 500, 1000, 2500),
    )
    if err != nil { return nil, err }

    return &Instruments{OrdersPlaced: placed, PaymentDuration: duration}, nil
}
```

### USE Method for Service Metrics

Always emit metrics covering the **USE Method** for every resource:

| Resource | Utilization | Saturation | Errors |
|---|---|---|---|
| HTTP server | `http.active_requests` | `http.queue_depth` | `http.errors_total` |
| SQS consumer | `sqs.in_flight_messages` | `sqs.lag_seconds` | `sqs.process_failures` |
| DB pool | `db.pool.in_use_connections` | `db.pool.wait_duration` | `db.errors_total` |
| Lambda | (N/A — managed) | `lambda.throttles_total` | `lambda.errors_total` |

### RED Method for Endpoints

For every HTTP/gRPC endpoint emit:
- **R**ate: `http.requests_total{method, path, status}` — counter
- **E**rrors: `http.errors_total{method, path, error_type}` — counter
- **D**uration: `http.request_duration_ms{method, path, status}` — histogram

---

## Phase 4 — CloudWatch Alarms & Dashboards

### Alarm Definitions (Terraform)

```hcl
# alarm-orders-error-rate.tf
resource "aws_cloudwatch_metric_alarm" "order_error_rate" {
  alarm_name          = "${var.service}-order-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 1   # 1% error rate

  metric_query {
    id          = "error_rate"
    expression  = "errors / requests * 100"
    return_data = true
  }
  metric_query {
    id = "errors"
    metric { metric_name = "orders.http.errors_total" ... }
  }
  metric_query {
    id = "requests"
    metric { metric_name = "orders.http.requests_total" ... }
  }

  alarm_actions = [var.pagerduty_sns_arn]
  tags          = local.finops_tags
}
```

### SLO Definition

Define SLOs explicitly in code comments and runbooks:

```
Service: Orders API
SLI: HTTP 5xx error rate on POST /orders
SLO: < 0.1% error rate over a 30-day rolling window
Error Budget: 0.1% × 30d × 24h × 60m = 43.2 minutes of downtime allowed
Burn Rate Alert: Page when 5% of monthly budget consumed in 1 hour
```

---

## Phase 5 — FinOps Practices

### 5.1 Mandatory Cost Tags

Every AWS resource created by a service must carry:

```go
// finopsTags returns the standard FinOps cost-allocation tags for a service.
// These tags are required on all AWS resources (Lambda, DynamoDB, SQS, ECS, etc.).
func finopsTags(cfg Config) map[string]string {
    return map[string]string{
        "service":     cfg.ServiceName,
        "team":        cfg.TeamName,
        "environment": cfg.Environment,
        "cost-center": cfg.CostCenter,   // e.g. "engineering/platform"
        "bounded-ctx": cfg.BoundedCtx,   // DDD context name
        "managed-by":  "terraform",
    }
}
```

Apply in Terraform:
```hcl
locals {
  finops_tags = {
    service     = var.service_name
    team        = var.team_name
    environment = var.environment
    cost-center = var.cost_center
    bounded-ctx = var.bounded_context
    managed-by  = "terraform"
  }
}
```

### 5.2 Lambda FinOps

```go
// Lambda memory optimization — run AWS Lambda Power Tuning tool first.
// Document the tuning result as a comment in the function configuration.
//
// Tuning result (2024-01-15):
//   Tested: 128, 256, 512, 1024 MB
//   Optimal: 512 MB → 45ms avg duration → $0.0000008 per invocation
//   At 128 MB: 180ms → $0.000000285 per invocation (slower, cheaper per ms but higher wall time)
//   Decision: 512 MB for latency SLA compliance
```

### 5.3 DynamoDB FinOps

```
Capacity mode decision:
- On-Demand: for bursty / unpredictable workloads (new services, < 5M req/month)
- Provisioned + Auto Scaling: for stable, predictable workloads (> 5M req/month)

TTL: always set TTL on transient data (sessions, idempotency keys, outbox records)
GSI discipline: every GSI costs; justify each one against query access patterns
Item size: keep items < 4KB to avoid paying for wasted read capacity units
```

### 5.4 Cost Anomaly Detection

```hcl
resource "aws_ce_anomaly_monitor" "service_monitor" {
  name              = "${var.service}-anomaly-monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_ce_anomaly_subscription" "alert" {
  name      = "${var.service}-cost-anomaly-alert"
  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
      values        = ["10"]  # Alert if anomaly > $10
      match_options = ["GREATER_THAN_OR_EQUAL"]
    }
  }
  monitor_arn_list = [aws_ce_anomaly_monitor.service_monitor.arn]
  subscriber {
    address = var.finops_email
    type    = "EMAIL"
  }
}
```

---

## Observability Checklist

- [ ] Structured JSON logging via `slog` — no `fmt.Println` in production paths
- [ ] Every log entry includes `traceId`, `spanId`, `requestId`
- [ ] OTEL TracerProvider initialised at startup with X-Ray ID generator
- [ ] Every use case method creates and closes a span with relevant attributes
- [ ] Errors recorded on spans with `span.RecordError()` and `codes.Error` status
- [ ] RED metrics emitted for every HTTP and gRPC endpoint
- [ ] USE metrics emitted for every managed resource (SQS, DB pool, cache)
- [ ] CloudWatch Alarms defined for error rate, latency p99, and SQS lag
- [ ] SLO defined with error budget and burn rate alerting
- [ ] FinOps tags applied to all AWS resources
- [ ] Lambda memory tuned with Power Tuning tool; result documented
- [ ] DynamoDB TTL set on all transient data tables
- [ ] Cost anomaly detection configured with $10 threshold alert
